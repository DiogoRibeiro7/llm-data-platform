from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from llm_observability_analytics.reports.specs import ReportSpec


def test_report_spec_dataclass_fields() -> None:
    spec = ReportSpec(report_name="latency", period_start="2026-01-01", period_end="2026-01-31")

    assert spec.report_name == "latency"
    assert spec.period_start == "2026-01-01"
    assert spec.period_end == "2026-01-31"


def test_report_spec_is_frozen_and_slotted() -> None:
    spec = ReportSpec(report_name="traffic", period_start="2026-02-01", period_end="2026-02-29")

    with pytest.raises(FrozenInstanceError):
        spec.report_name = "changed"  # type: ignore[misc]

    with pytest.raises((AttributeError, TypeError)):
        spec.extra = "x"  # type: ignore[attr-defined]
