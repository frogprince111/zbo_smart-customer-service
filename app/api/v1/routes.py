from fastapi import APIRouter, Request, WebSocket

from app.api.v1.schemas import ChatRequest, ChatResponse, HealthResponse
from app.core.config import get_settings

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", app=settings.app_name)


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    response = await request.app.state.agent.handle(payload.sender_id, payload.message)
    return ChatResponse(sender_id=payload.sender_id, message=response)


@router.get("/providers/status")
async def provider_status() -> dict[str, str]:
    return {"llm": "mock", "business": "mock", "handoff": "mock", "vector_store": "memory"}


@router.post("/knowledge/import")
async def import_knowledge() -> dict[str, str]:
    return {"status": "accepted", "message": "Mock 模式下知识库从 data/knowledge 自动加载。"}


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket) -> None:
    await websocket.accept()
    sender_id = websocket.query_params.get("sender_id", "websocket_user")
    while True:
        message = await websocket.receive_text()
        response = await websocket.app.state.agent.handle(sender_id, message)
        await websocket.send_json({"sender_id": sender_id, "message": response})

