from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class HttpEndpointConfig(BaseModel):
    """外部 HTTP 接口的通用配置。"""

    enabled: bool = False
    url: str = ""
    method: str = "GET"
    api_key: str = ""
    timeout: int = 15
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] = Field(default_factory=dict)
    response_mapping: dict[str, str] = Field(default_factory=dict)


class LLMEndpointConfig(HttpEndpointConfig):
    model: str = ""
    content_path: str = ""


class OrderQueryConfig(HttpEndpointConfig):
    status_mapping: dict[str, str] = Field(default_factory=dict)


class BusinessInterfacesConfig(BaseModel):
    order_query: OrderQueryConfig = Field(default_factory=OrderQueryConfig)


class HandoffInterfacesConfig(BaseModel):
    create_ticket: HttpEndpointConfig = Field(default_factory=HttpEndpointConfig)


class KnowledgeInterfacesConfig(BaseModel):
    import_documents: HttpEndpointConfig = Field(default_factory=HttpEndpointConfig)


class EmbeddingInterfacesConfig(HttpEndpointConfig):
    model: str = ""
    dimension: int = 1024


class ExternalInterfacesConfig(BaseModel):
    """集中管理所有真实外部接口配置。"""

    llm: LLMEndpointConfig = Field(default_factory=LLMEndpointConfig)
    business: BusinessInterfacesConfig = Field(default_factory=BusinessInterfacesConfig)
    handoff: HandoffInterfacesConfig = Field(default_factory=HandoffInterfacesConfig)
    knowledge: KnowledgeInterfacesConfig = Field(default_factory=KnowledgeInterfacesConfig)
    embedding: EmbeddingInterfacesConfig = Field(default_factory=EmbeddingInterfacesConfig)


def load_external_interfaces_config(path: str) -> ExternalInterfacesConfig:
    config_path = Path(path)
    if not config_path.exists():
        return ExternalInterfacesConfig()
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return ExternalInterfacesConfig.model_validate(payload)


def get_by_path(payload: Any, path: str, default: Any = "") -> Any:
    """按 data.order.id 这种路径从 JSON 中取值。"""

    if not path:
        return payload
    current = payload
    for part in path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return default
            continue
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def render_template(value: Any, variables: dict[str, Any]) -> Any:
    """递归替换字符串模板中的 {name} 占位符。"""

    if isinstance(value, str):
        rendered = value
        for key, variable_value in variables.items():
            rendered = rendered.replace("{" + key + "}", str(variable_value))
        return rendered
    if isinstance(value, list):
        return [render_template(item, variables) for item in value]
    if isinstance(value, dict):
        return {key: render_template(item, variables) for key, item in value.items()}
    return value

