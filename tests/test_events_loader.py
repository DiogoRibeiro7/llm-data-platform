from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from llm_observability_analytics.contracts.models import (
    LLMInteractionEvent,
    ModelExecutionContext,
    TokenUsageRecord,
    LatencyRecord,
    SourceGroundingReference,
    RetrievalTraceEvent,
)
from llm_observability_analytics.events.loader import (
    load_interaction_events,
    load_retrieval_trace_events,
)


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _make_interaction(query_id: str, trace_id: str) -> LLMInteractionEvent:
    mc = ModelExecutionContext(
        query_id=query_id,
        trace_id=trace_id,
        model_version="m-v",
        dataset_version=None,
        provider="prov",
        model_name="name",
    )
    tu = TokenUsageRecord(
        query_id=query_id,
        trace_id=trace_id,
        model_version="m-v",
        dataset_version=None,
        input_tokens=1,
        output_tokens=2,
        recorded_at=datetime.now(timezone.utc),
    )
    lat = LatencyRecord(
        query_id=query_id,
        trace_id=trace_id,
        request_timestamp=datetime.now(timezone.utc),
        response_timestamp=datetime.now(timezone.utc),
        latency_ms=123,
    )
    ref = SourceGroundingReference(
        query_id=query_id, trace_id=trace_id, document_id="doc1", chunk_id="chk1"
    )
    return LLMInteractionEvent(
        query_id=query_id,
        trace_id=trace_id,
        request_timestamp=datetime.now(timezone.utc),
        response_timestamp=datetime.now(timezone.utc),
        prompt_text="p",
        response_text="r",
        model_context=mc,
        token_usage=tu,
        latency=lat,
        retrieval_references=[ref],
    )


def _make_retrieval(query_id: str, trace_id: str) -> RetrievalTraceEvent:
    ref = SourceGroundingReference(
        query_id=query_id, trace_id=trace_id, document_id="doc1", chunk_id="chk1"
    )
    return RetrievalTraceEvent(
        query_id=query_id,
        trace_id=trace_id,
        retrieval_timestamp=datetime.now(timezone.utc),
        query_text="hello",
        retrieval_system="r",
        top_k=1,
        references=[ref],
    )


def test_load_interaction_events_success(tmp_path: Path) -> None:
    p = tmp_path / "interactions.jsonl"
    evt = _make_interaction("q1", "t1")
    p.write_text(evt.to_json() + "\n", encoding="utf-8")

    out = load_interaction_events(p, max_events=10)
    assert len(out) == 1
    assert out[0].query_id == "q1"


def test_load_retrieval_trace_events_success(tmp_path: Path) -> None:
    p = tmp_path / "retrieval.jsonl"
    evt = _make_retrieval("q2", "t2")
    p.write_text(evt.to_json() + "\n", encoding="utf-8")

    out = load_retrieval_trace_events(p, max_events=10)
    assert len(out) == 1
    assert out[0].query_id == "q2"


def test_load_invalid_json_raises(tmp_path: Path) -> None:
    p = tmp_path / "broken.jsonl"
    p.write_text("{not-json}\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_interaction_events(p, max_events=10)

