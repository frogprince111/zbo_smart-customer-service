import pytest

from app.core.config import Settings
from app.llm.parser import CommandParser
from app.llm.provider import MockLLMProvider
from app.providers.business import MockBusinessProvider
from app.providers.factory import create_agent


@pytest.mark.asyncio
async def test_order_query_full_flow() -> None:
    agent = await create_agent(Settings())
    assert await agent.handle("u1", "帮我查订单") == "请提供订单号"
    assert await agent.handle("u1", "10001") == "订单已发货，物流单号为 SF10001"


@pytest.mark.asyncio
async def test_knowledge_qa_flow() -> None:
    agent = await create_agent(Settings())
    response = await agent.handle("u2", "你们支持七天无理由退货吗")
    assert "支持七天无理由退货" in response
    assert "来源：" in response


@pytest.mark.asyncio
async def test_knowledge_interrupts_business_flow_then_resume() -> None:
    agent = await create_agent(Settings())
    assert await agent.handle("u3", "帮我查订单") == "请提供订单号"
    assert "来源：" in await agent.handle("u3", "你们支持七天无理由退货吗")
    assert await agent.handle("u3", "10001") == "订单已发货，物流单号为 SF10001"


@pytest.mark.asyncio
async def test_user_cancel_flow() -> None:
    agent = await create_agent(Settings())
    await agent.handle("u4", "帮我查订单")
    assert await agent.handle("u4", "取消") == "已取消当前流程。"


@pytest.mark.asyncio
async def test_handoff() -> None:
    agent = await create_agent(Settings())
    response = await agent.handle("u5", "转人工客服")
    assert "已创建模拟人工客服工单" in response


@pytest.mark.asyncio
async def test_external_failure_degrades() -> None:
    agent = await create_agent(Settings())
    agent.actions.get("query_order").business_provider = MockBusinessProvider(fail=True)  # type: ignore[attr-defined]
    await agent.handle("u6", "帮我查订单")
    response = await agent.handle("u6", "10001")
    assert "订单系统暂时不可用" in response


@pytest.mark.asyncio
async def test_illegal_llm_json_fallback() -> None:
    agent = await create_agent(Settings())
    agent.parser = CommandParser(MockLLMProvider(illegal_json=True))
    response = await agent.handle("u7", "bad_json")
    assert "暂时没有理解" in response

