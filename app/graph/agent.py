from app.actions.registry import ActionRegistry
from app.domain.models import Event, EventType
from app.domain.store import TrackerStore
from app.flows.executor import FlowExecutor
from app.flows.models import Flow
from app.llm.parser import CommandParser
from app.llm.processor import CommandProcessor
from app.policies.base import PolicyDecisionType
from app.policies.ensemble import PolicyEnsemble
from app.rag.service import RAGService


class Agent:
    """主 Agent，承担 LangGraph 节点编排的最小安全实现。"""

    def __init__(
        self,
        tracker_store: TrackerStore,
        parser: CommandParser,
        command_processor: CommandProcessor,
        policies: PolicyEnsemble,
        flows: dict[str, Flow],
        flow_executor: FlowExecutor,
        actions: ActionRegistry,
        rag: RAGService,
    ):
        self.tracker_store = tracker_store
        self.parser = parser
        self.command_processor = command_processor
        self.policies = policies
        self.flows = flows
        self.flow_executor = flow_executor
        self.actions = actions
        self.rag = rag

    async def handle(self, sender_id: str, message: str) -> str:
        tracker = await self.tracker_store.get_or_create(sender_id)
        tracker.add_event(Event(type=EventType.user, text=message))
        command = await self.parser.parse(message)
        tracker.add_event(Event(type=EventType.command, data=command.model_dump()))
        self.command_processor.apply(command, tracker)
        decision = await self.policies.decide(command, tracker)
        response = await self._execute_decision(decision.type, decision.flow_id, tracker, message)
        tracker.add_event(Event(type=EventType.assistant, text=response))
        await self.tracker_store.save(tracker)
        return response

    async def _execute_decision(
        self, decision_type: PolicyDecisionType, flow_id: str | None, tracker, message: str
    ) -> str:
        if decision_type == PolicyDecisionType.cancel:
            tracker.stack.clear()
            return "已取消当前流程。"
        if decision_type == PolicyDecisionType.rag:
            return await self.rag.answer(message)
        if decision_type == PolicyDecisionType.handoff:
            return (await self.actions.get("create_handoff_ticket").run(tracker, {"message": message})).text
        if decision_type == PolicyDecisionType.start_flow and flow_id in self.flows:
            return (await self.flow_executor.start(self.flows[flow_id], tracker)).text
        if decision_type == PolicyDecisionType.continue_flow and flow_id in self.flows:
            return (await self.flow_executor.continue_flow(self.flows[flow_id], tracker)).text
        return "抱歉，我暂时没有理解你的问题。你可以说“帮我查订单”或“转人工客服”。"

