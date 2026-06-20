from app.graph.state import AgentState


async def passthrough_node(state: AgentState) -> AgentState:
    return state

