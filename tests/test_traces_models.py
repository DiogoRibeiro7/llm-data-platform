from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from llm_observability_analytics.traces.models import TraceReference


def test_trace_reference_fields() -> None:
    trace = TraceReference(trace_id="t1", query_id="q1")

    assert trace.trace_id == "t1"
    assert trace.query_id == "q1"


def test_trace_reference_is_frozen_and_slotted() -> None:
    trace = TraceReference(trace_id="t1", query_id="q1")

    with pytest.raises(FrozenInstanceError):
        trace.trace_id = "t2"  # type: ignore[misc]

    with pytest.raises((AttributeError, TypeError)):
        trace.extra = "x"  # type: ignore[attr-defined]
