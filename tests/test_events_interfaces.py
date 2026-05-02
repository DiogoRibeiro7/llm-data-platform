from __future__ import annotations

from datetime import UTC, datetime

import pytest

from llm_observability_analytics.contracts.models import (
    LatencyRecord,
    LLMInteractionEvent,
    ModelExecutionContext,
    RetrievalTraceEvent,
    TokenUsageRecord,
)
from llm_observability_analytics.events.interfaces import EventSink


def _sample_interaction() -> LLMInteractionEvent:
    ts = datetime.now(UTC)
    model_context = ModelExecutionContext(
        query_id="q1",
        trace_id="t1",
        model_version="model-v1",
        dataset_version=None,
        provider="provider",
        model_name="name",
    )
    token_usage = TokenUsageRecord(
        query_id="q1",
        trace_id="t1",
        model_version="model-v1",
        dataset_version=None,
        input_tokens=1,
        output_tokens=1,
        recorded_at=ts,
    )
    latency = LatencyRecord(
        query_id="q1",
        trace_id="t1",
        request_timestamp=ts,
        response_timestamp=ts,
        latency_ms=5,
    )
    return LLMInteractionEvent(
        query_id="q1",
        trace_id="t1",
        request_timestamp=ts,
        response_timestamp=ts,
        prompt_text="prompt",
        response_text="response",
        model_context=model_context,
        token_usage=token_usage,
        latency=latency,
        retrieval_references=[],
    )


def _sample_retrieval() -> RetrievalTraceEvent:
    ts = datetime.now(UTC)
    return RetrievalTraceEvent(
        query_id="q2",
        trace_id="t2",
        retrieval_timestamp=ts,
        query_text="hello",
        retrieval_system="search",
        top_k=3,
        references=[],
    )


def test_event_sink_is_abstract() -> None:
    with pytest.raises(TypeError):
        EventSink()


def test_event_sink_dummy_implementation_emits_events() -> None:
    class InMemorySink(EventSink):
        def __init__(self) -> None:
            self.events: list[object] = []

        def emit(self, event: object) -> None:
            self.events.append(event)

    sink = InMemorySink()
    interaction = _sample_interaction()
    retrieval = _sample_retrieval()

    sink.emit(interaction)
    sink.emit(retrieval)

    assert sink.events == [interaction, retrieval]
