from pathlib import Path

from app.actions.builtin import HandoffAction, QueryOrderAction
from app.actions.registry import ActionRegistry
from app.core.config import Settings
from app.core.interface_config import ExternalInterfacesConfig, load_external_interfaces_config
from app.domain.store import MemoryTrackerStore, TrackerStore
from app.flows.conditions import ConditionEvaluator
from app.flows.executor import FlowExecutor
from app.flows.loader import FlowLoader
from app.flows.validator import FlowValidator
from app.graph.agent import Agent
from app.llm.parser import CommandParser
from app.llm.processor import CommandProcessor
from app.llm.provider import HttpLLMProvider, LLMProvider, MockLLMProvider
from app.policies.builtin import CommandPolicy, FallbackPolicy
from app.policies.ensemble import PolicyEnsemble
from app.providers.business import BusinessProvider, HttpBusinessProvider, MockBusinessProvider
from app.providers.handoff import HandoffProvider, MockHandoffProvider, WebhookHandoffProvider
from app.rag.document import Chunker, DocumentReader, TextCleaner
from app.rag.providers import MockEmbeddingProvider, MockRerankProvider
from app.rag.retriever import Retriever
from app.rag.service import RAGService
from app.rag.vector_store import MemoryVectorStore, VectorStore


def create_llm_provider(settings: Settings, interfaces: ExternalInterfacesConfig) -> LLMProvider:
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    return HttpLLMProvider(interfaces.llm)


def create_business_provider(settings: Settings, interfaces: ExternalInterfacesConfig) -> BusinessProvider:
    if settings.business_provider == "mock":
        return MockBusinessProvider()
    return HttpBusinessProvider(
        settings.business_api_base_url,
        settings.business_api_key,
        settings.business_api_timeout,
        interfaces.business.order_query,
    )


def create_handoff_provider(settings: Settings, interfaces: ExternalInterfacesConfig) -> HandoffProvider:
    if settings.handoff_provider == "mock":
        return MockHandoffProvider()
    return WebhookHandoffProvider(
        settings.handoff_webhook_url,
        settings.handoff_api_key,
        interfaces.handoff.create_ticket,
    )


def create_tracker_store(settings: Settings) -> TrackerStore:
    return MemoryTrackerStore()


async def create_rag_service(settings: Settings) -> RAGService:
    vector_store: VectorStore = MemoryVectorStore()
    embedding = MockEmbeddingProvider(settings.embedding_dimension)
    reader = DocumentReader()
    cleaner = TextCleaner()
    docs = reader.read_directory(Path("data/knowledge"))
    cleaned = [doc.model_copy(update={"text": cleaner.clean(doc.text)}) for doc in docs]
    chunks = Chunker(settings.chunk_size, settings.chunk_overlap).split(cleaned)
    for chunk in chunks:
        await embedding.embed(chunk.text)
    await vector_store.add(chunks)
    retriever = Retriever(
        vector_store=vector_store,
        reranker=MockRerankProvider(),
        top_k=settings.retrieval_top_k,
        top_n=settings.rerank_top_n,
        threshold=settings.retrieval_score_threshold,
    )
    return RAGService(retriever)


async def create_agent(settings: Settings) -> Agent:
    interfaces = load_external_interfaces_config(settings.external_interfaces_config)
    llm = create_llm_provider(settings, interfaces)
    business = create_business_provider(settings, interfaces)
    handoff = create_handoff_provider(settings, interfaces)
    actions = ActionRegistry()
    actions.register(QueryOrderAction(business))
    actions.register(HandoffAction(handoff))
    flows = FlowLoader(settings.flow_dir).load_all()
    FlowValidator().validate_all(flows)
    executor = FlowExecutor(actions, ConditionEvaluator())
    return Agent(
        tracker_store=create_tracker_store(settings),
        parser=CommandParser(llm),
        command_processor=CommandProcessor(),
        policies=PolicyEnsemble([CommandPolicy(), FallbackPolicy()]),
        flows=flows,
        flow_executor=executor,
        actions=actions,
        rag=await create_rag_service(settings),
    )
