from fastapi.testclient import TestClient

from app.main import app


def test_chat_api() -> None:
    with TestClient(app) as client:
        health = client.get("/api/v1/health")
        assert health.status_code == 200
        response = client.post(
            "/api/v1/chat",
            json={"sender_id": "api_user", "message": "帮我查一下订单"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "请提供订单号"

