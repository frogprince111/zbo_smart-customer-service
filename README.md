# smart-customer-service

企业级智能问答助手示例项目，支持 FastAPI、Flow、Action、Policy、Mock LLM、Mock 业务系统、RAG 引用、人工客服转接、PostgreSQL/pgvector/Redis 的 Docker Compose 部署骨架。

## 核心架构图

```mermaid
flowchart LR
  A[用户渠道] --> B[FastAPI]
  B --> C[Agent]
  C --> D[LangGraph]
  D --> E[Command]
  E --> F[Policy]
  F --> G[Flow/Action/RAG]
  G --> H[外部业务系统]
  G --> I[NLG]
  I --> A
```

## 请求处理流程

用户请求进入 `/api/v1/chat` 后，Agent 读取 Tracker，调用 CommandParser 识别意图，再由 PolicyEnsemble 决定进入 Flow、RAG、人工转接或兜底回复。FlowExecutor 负责收集 Slot 并执行 Action，RAGService 负责检索知识并返回来源。

## 目录说明

- `app/api`：REST 和 WebSocket API。
- `app/core`：配置、日志、统一异常。
- `app/domain`：Tracker、Slot、Event、DialogueStack。
- `app/flows`：Flow 模型、YAML Loader、Validator、Executor。
- `app/actions`：Action 接口、Registry、内置动作。
- `app/policies`：Policy 接口和策略集成。
- `app/llm`：LLM Provider、Prompt、CommandParser。
- `app/rag`：文档读取、Chunk、检索、重排、引用格式。
- `app/providers`：Provider Factory、业务系统、人工客服。
- `flows`：业务流程 YAML。
- `data/knowledge`：示例知识库。
- `tests`：单元、集成、E2E 测试。

## 本地启动方法

```bash
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

真实外部接口集中配置模板在 `config/external_interfaces.example.yaml`。需要接真实接口时：

```bash
cp config/external_interfaces.example.yaml config/external_interfaces.yaml
```

然后在 `.env` 中把对应 Provider 改成 `http` 或 `webhook`，并在 `config/external_interfaces.yaml` 里填写真实 URL、API Key、请求体和返回字段映射。

不使用 `uv` 时：

```bash
pip install -e .
uvicorn app.main:app --reload
```

## Docker 启动方法

```bash
cp .env.example .env
docker compose up --build
```

Docker Compose 包含应用、PostgreSQL pgvector 镜像和 Redis。

## 接入 DeepSeek

在 `.env` 中配置：

```env
LLM_PROVIDER=deepseek
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=你的密钥
LLM_MODEL=deepseek-chat
```

然后在 `app/providers/factory.py` 中补充 DeepSeek Provider 适配器。业务代码不需要直接实例化 Provider。

## 接入 Qwen

```env
LLM_PROVIDER=qwen
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=你的密钥
LLM_MODEL=qwen-plus
```

新增 Qwen Provider 后只在 Factory 中切换。

## 接入 OpenAI

```env
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=你的密钥
LLM_MODEL=gpt-4.1-mini
```

## 接入 Ollama

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=qwen2.5
```

## 接入 BGE-M3

```env
EMBEDDING_PROVIDER=bge-m3
EMBEDDING_MODEL=bge-m3
EMBEDDING_BASE_URL=http://你的-embedding-service
EMBEDDING_DIMENSION=1024
```

## 切换 pgvector

```env
VECTOR_STORE=pgvector
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/customer_service
```

当前提供 MemoryVectorStore 的最小实现，pgvector 接口位置在 `app/rag/vector_store.py`。

## 接入真实订单系统

配置：

```env
BUSINESS_PROVIDER=http
BUSINESS_API_BASE_URL=https://orders.example.com
BUSINESS_API_KEY=你的业务系统密钥
EXTERNAL_INTERFACES_CONFIG=config/external_interfaces.yaml
```

然后复制并修改 `config/external_interfaces.yaml` 里的 `business.order_query`，填写 URL、headers、body 和 `response_mapping`。Action 和 Flow 无需修改。

## 接入人工客服 Webhook

```env
HANDOFF_PROVIDER=webhook
HANDOFF_WEBHOOK_URL=https://support.example.com/webhook
HANDOFF_API_KEY=你的密钥
EXTERNAL_INTERFACES_CONFIG=config/external_interfaces.yaml
```

然后复制并修改 `config/external_interfaces.yaml` 里的 `handoff.create_ticket`。

## 新增 Flow

在 `flows/` 新增 YAML，例如定义 `id`、`name`、`trigger_commands` 和 `steps`。步骤支持 `slot`、`action`、`message`。

## 新增 Slot

在 Flow 的 `slot` 步骤声明 Slot 名称和提示语；需要复杂校验时扩展 `app/domain/models.py` 的 Slot 或新增 Slot Validator。

## 新增 Action

继承 `app.actions.base.Action`，实现 `run`，再在 `app/providers/factory.py` 的 ActionRegistry 注册。

## 新增 Policy

继承 `app.policies.base.Policy`，实现 `decide`，加入 `PolicyEnsemble`。

## 导入知识文档

将 Markdown 文件放入 `data/knowledge/`，Mock 模式启动时自动读取。生产环境可把 `/api/v1/knowledge/import` 扩展为上传、切分、入库流程。

## API 调用示例

```bash
curl http://localhost:8000/api/v1/health

curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"sender_id":"user_001","message":"帮我查一下订单"}'
```

## 测试方法

```bash
python -m compileall app
pytest
ruff check .
```

## 常见问题

1. Mock 模式是否需要密钥？不需要，默认 `LLM_PROVIDER=mock`、`BUSINESS_PROVIDER=mock`。
2. 为什么真实 Provider 还没有直接请求外部服务？项目提供稳定接口和安全最小实现，真实协议需要按你的系统字段补适配器。
3. Flow 被知识问答打断能恢复吗？可以，RAG 回复不会清空 DialogueStack。
4. 如何处理 LLM 非法 JSON？CommandParser 会降级为 unknown，并触发兜底回复。
