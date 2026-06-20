from app.core.interface_config import get_by_path, load_external_interfaces_config, render_template


def test_load_external_interfaces_example() -> None:
    config = load_external_interfaces_config("config/external_interfaces.example.yaml")
    assert config.llm.url
    assert config.business.order_query.url
    assert config.handoff.create_ticket.url


def test_render_template() -> None:
    rendered = render_template(
        {
            "url": "https://example.com/orders/{order_id}",
            "headers": {"Authorization": "Bearer {api_key}"},
        },
        {"order_id": "10001", "api_key": "secret"},
    )
    assert rendered["url"] == "https://example.com/orders/10001"
    assert rendered["headers"]["Authorization"] == "Bearer secret"


def test_get_by_path() -> None:
    payload = {"data": {"items": [{"trackingNo": "SF10001"}]}}
    assert get_by_path(payload, "data.items.0.trackingNo") == "SF10001"
    assert get_by_path(payload, "data.missing", "fallback") == "fallback"

