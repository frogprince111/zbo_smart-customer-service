from app.actions.base import ActionResult
from app.actions.registry import ActionRegistry
from app.domain.models import StackFrame, Tracker
from app.flows.conditions import ConditionEvaluator
from app.flows.models import Flow, FlowStepType


class FlowExecutor:
    """执行当前 Flow，遇到缺失 Slot 时暂停等待用户补充。"""

    def __init__(self, actions: ActionRegistry, condition_evaluator: ConditionEvaluator):
        self.actions = actions
        self.condition_evaluator = condition_evaluator

    async def start(self, flow: Flow, tracker: Tracker) -> ActionResult:
        tracker.stack.push(StackFrame(flow_id=flow.id))
        return await self.continue_flow(flow, tracker)

    async def continue_flow(self, flow: Flow, tracker: Tracker) -> ActionResult:
        frame = tracker.stack.current()
        if frame is None:
            return ActionResult(text="", done=True)
        messages: list[str] = []
        while frame.step_index < len(flow.steps):
            step = flow.steps[frame.step_index]
            frame.step_index += 1
            if not self.condition_evaluator.evaluate(step.condition, tracker):
                continue
            if step.type == FlowStepType.slot:
                slot_name = step.slot or ""
                if tracker.slots.get(slot_name) in (None, ""):
                    frame.step_index -= 1
                    return ActionResult(text=step.prompt or f"请提供{slot_name}", done=False)
                continue
            if step.type == FlowStepType.message:
                if step.text:
                    messages.append(step.text)
                continue
            if step.type == FlowStepType.action and step.name:
                result = await self.actions.get(step.name).run(tracker, step.params)
                messages.append(result.text)
        tracker.stack.pop()
        return ActionResult(text="\n".join(part for part in messages if part), done=True)

