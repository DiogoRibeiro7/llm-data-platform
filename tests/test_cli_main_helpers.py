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


def test_validate_config_cmd_valid_and_invalid(tmp_path: Path) -> None:
    valid = tmp_path / "valid.yaml"
    invalid = tmp_path / "invalid.yaml"
    valid.write_text(
        """
events:
  interactions_path: interactions.jsonl
  retrievals_path: retrievals.jsonl
  max_events: 10
output:
  validated_events_path: validated.jsonl
  summary_path: summary.json
  run_result_path: result.json
""",
        encoding="utf-8",
    )
    invalid.write_text(
        """
events:
  interactions_path: interactions.jsonl
output:
  summary_path: summary.json
""",
        encoding="utf-8",
    )

    assert cli_main.validate_config_cmd(str(valid)) == 0
    assert cli_main.validate_config_cmd(str(invalid)) == 1


def test_diff_contracts_cmd_non_breaking_and_breaking(tmp_path: Path) -> None:
    old = tmp_path / "old.json"
    new_non_breaking = tmp_path / "new_non_breaking.json"
    new_breaking = tmp_path / "new_breaking.json"

    old.write_text('{"field":"value","count":1}', encoding="utf-8")
    new_non_breaking.write_text('{"field":"value","count":1,"new_field":"x"}', encoding="utf-8")
    new_breaking.write_text('{"field":"value","count":"one"}', encoding="utf-8")

    assert cli_main.diff_contracts_cmd(str(old), str(new_non_breaking)) == 0
    assert cli_main.diff_contracts_cmd(str(old), str(new_breaking)) == 1


def test_visualize_pipeline_cmd(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    config = tmp_path / "config.yaml"
    config.write_text(
        """
events:
  interactions_path: interactions.jsonl
  retrievals_path: retrievals.jsonl
output:
  validated_events_path: validated.jsonl
  summary_path: summary.json
  run_result_path: result.json
""",
        encoding="utf-8",
    )

    assert cli_main.visualize_pipeline_cmd(str(config)) == 0
    out = capsys.readouterr().out
    assert "graph TD" in out
    assert "Interactions" in out


def test_coverage_report_cmd_failure_branch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class _Result:
        returncode = 1
        stdout = "failed"

    monkeypatch.setattr(cli_main.subprocess, "run", lambda *args, **kwargs: _Result())
    assert cli_main.coverage_report_cmd() == 1
    out = capsys.readouterr().out
    assert "Some tests failed." in out
