from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from llm_observability_analytics.cli import main as cli_main


class _ObjWithToDict:
    def to_dict(self) -> dict[str, object]:
        return {"a": 1}


class _ObjWithBadToDict:
    def to_dict(self) -> object:
        return [1, 2, 3]


def test_to_dict_supports_objects_and_dicts() -> None:
    assert cli_main._to_dict(_ObjWithToDict()) == {"a": 1}
    assert cli_main._to_dict({"k": "v"}) == {"k": "v"}
    assert cli_main._to_dict(_ObjWithBadToDict()) == {}
    assert cli_main._to_dict("nope") == {}


def test_detect_schema_groups_field_types() -> None:
    schema = cli_main.detect_schema([
        {"x": 1, "y": "a"},
        {"x": 2.5, "y": "b"},
    ])
    assert schema["x"] == ["float", "int"]
    assert schema["y"] == ["str"]


def test_filter_events_by_time_and_passthrough() -> None:
    ts1 = datetime(2026, 1, 1, tzinfo=UTC).isoformat()
    ts2 = datetime(2026, 2, 1, tzinfo=UTC).isoformat()
    events = [{"request_timestamp": ts1}, {"request_timestamp": ts2}]

    assert cli_main.filter_events_by_time(events, None, None, ["request_timestamp"]) == events

    filtered = cli_main.filter_events_by_time(
        events,
        "2026-01-15T00:00:00+00:00",
        "2026-02-15T00:00:00+00:00",
        ["request_timestamp"],
    )
    assert filtered == [{"request_timestamp": ts2}]


class _LatencyObj:
    def __init__(self, latency_ms: int, payload: dict[str, object]) -> None:
        self.latency_ms = latency_ms
        self._payload = payload

    def to_dict(self) -> dict[str, object]:
        return self._payload


def test_detect_anomalies_latency_and_required_fields() -> None:
    events = [_LatencyObj(10, {"query_id": "q"}) for _ in range(10)]
    events.append(_LatencyObj(1000, {"query_id": "q"}))
    anomalies = cli_main.detect_anomalies(events, latency_field="latency_ms", required_fields=["trace_id"])

    reasons = [reason for _, reason in anomalies]
    assert any(reason == "outlier latency_ms=1000" for reason in reasons)
    assert any(reason == "missing or empty field: trace_id" for reason in reasons)


def test_run_subcommand_from_argv_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["prog", "coverage-report"])
    monkeypatch.setattr(cli_main, "coverage_report_cmd", lambda: 7)
    assert cli_main._run_subcommand_from_argv() == 7

    monkeypatch.setattr(sys, "argv", ["prog", "diff-contracts"])
    assert cli_main._run_subcommand_from_argv() == 2

    monkeypatch.setattr(sys, "argv", ["prog", "unknown"])
    assert cli_main._run_subcommand_from_argv() is None


def test_diff_contracts_cmd_rejects_non_mapping(tmp_path: Path) -> None:
    old = tmp_path / "old.yaml"
    new = tmp_path / "new.yaml"
    old.write_text("[]", encoding="utf-8")
    new.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="Contract payload must be a mapping"):
        cli_main.diff_contracts_cmd(str(old), str(new))
