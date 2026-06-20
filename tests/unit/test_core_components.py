import pytest

from app.actions.base import Action, ActionResult
from app.actions.registry import ActionRegistry
from app.core.errors import FlowError, ValidationError
from app.domain.models import DialogueStack, Slot, StackFrame, Tracker
from app.flows.conditions import ConditionEvaluator
from app.flows.executor import FlowExecutor
from app.flows.loader import FlowLoader
from app.flows.models import Flow
from app.flows.validator import FlowValidator
from app.llm.models import Command, CommandType
from app.llm.parser import CommandParser
from app.llm.provider import MockLLMProvider
from app.policies.builtin import CommandPolicy, FallbackPolicy
from app.policies.ensemble import PolicyEnsemble
from app.providers.business import MockBusinessProvider
from app.rag.models import Chunk
from app.rag.service import RAGService


class EchoAction(Action):
    name = "echo"

    async def run(self, tracker: Tracker, params: dict | None = None) -> ActionResult:
        return ActionResult(text=f"echo:{tracker.slots.get('foo')}")


def test_slot_filled() -> None:
    assert not Slot(name="order_id").filled
    assert Slot(name="order_id", value="10001").filled


def test_dialogue_stack() -> None:
    stack = DialogueStack()
    stack.push(StackFrame(flow_id="f1"))
    assert stack.current().flow_id == "f1"
    assert stack.pop().flow_id == "f1"
    assert stack.current() is None


def test_flow_loader_and_validator() -> None:
    flows = FlowLoader("flows").load_all()
    FlowValidator().validate_all(flows)
    assert "query_order" in flows


def test_flow_validator_rejects_empty() -> None:
    with pytest.raises(FlowError):
        FlowValidator().validate(Flow(id="bad", name="bad", steps=[]))


def test_condition_evaluator() -> None:
    tracker = Tracker(sender_id="u")
    tracker.set_slot("vip", "yes")
    evaluator = ConditionEvaluator()
    assert evaluator.evaluate("slot.vip", tracker)
    assert evaluator.evaluate("slot.vip == 'yes'", tracker)
    assert evaluator.evaluate("not slot.missing", tracker)


@pytest.mark.asyncio
async def test_flow_executor() -> None:
    registry = ActionRegistry()
    registry.register(EchoAction())
    flow = Flow.model_validate(
        {"id": "f", "name": "f", "steps": [{"type": "slot", "slot": "foo", "prompt": "need foo"}, {"type": "action", "name": "echo"}]}
    )
    tracker = Tracker(sender_id="u")
    executor = FlowExecutor(registry, ConditionEvaluator())
    assert (await executor.start(flow, tracker)).text == "need foo"
    tracker.set_slot("foo", "bar")
    assert (await executor.continue_flow(flow, tracker)).text == "echo:bar"


@pytest.mark.asyncio
async def test_policy_ensemble() -> None:
    decision = await PolicyEnsemble([CommandPolicy(), FallbackPolicy()]).decide(
        Command(type=CommandType.knowledge_qa), Tracker(sender_id="u")
    )
    assert decision.type.value == "rag"


def test_action_registry() -> None:
    registry = ActionRegistry()
    registry.register(EchoAction())
    assert registry.get("echo").name == "echo"
    with pytest.raises(ValidationError):
        registry.get("missing")


@pytest.mark.asyncio
async def test_mock_llm_provider_and_parser() -> None:
    parser = CommandParser(MockLLMProvider())
    command = await parser.parse("帮我查订单")
    assert command.type == CommandType.start_flow
    bad = await CommandParser(MockLLMProvider(illegal_json=True)).parse("anything")
    assert bad.type == CommandType.unknown


@pytest.mark.asyncio
async def test_mock_business_provider() -> None:
    provider = MockBusinessProvider()
    assert await provider.health_check()
    order = await provider.get_order("10001")
    assert order["tracking_no"] == "SF10001"


def test_rag_citation_format() -> None:
    service = RAGService(retriever=None)  # type: ignore[arg-type]
    chunk = Chunk(id="c1", text="退货政策正文", source="return_policy.md")
    assert service._format_citation(chunk).startswith("[return_policy.md]")

