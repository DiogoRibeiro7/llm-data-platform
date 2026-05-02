from __future__ import annotations

from typing import get_args

from llm_observability_analytics.contracts.entities import (
    EventEnvelope,
    LLMInteractionEvent,
    RetrievalTraceEvent,
    UserFeedbackEvent,
)


def test_event_envelope_alias_contains_expected_models() -> None:
    members = set(get_args(EventEnvelope))
    assert members == {LLMInteractionEvent, RetrievalTraceEvent, UserFeedbackEvent}


def test_contracts_entities_exports_expected_symbols() -> None:
    from llm_observability_analytics.contracts import entities

    assert entities.__all__ == [
        "EventEnvelope",
        "LLMInteractionEvent",
        "RetrievalTraceEvent",
        "UserFeedbackEvent",
    ]
