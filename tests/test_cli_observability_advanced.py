import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from llm_observability_analytics.cli import main as cli_main

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo_root() -> Path:
    return ROOT


def _run_cli(args: list[str], repo_root: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo_root / "src")
    return subprocess.run(
        [sys.executable, "-m", "llm_observability_analytics.cli.main", *args],
        capture_output=True,
        text=True,
        env=env,
    )


def _write_obs_config(tmp_path: Path, interactions_path: Path, retrievals_path: Path) -> Path:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
events:
  interactions_path: {interactions_path.as_posix()}
  retrievals_path: {retrievals_path.as_posix()}
  max_events: 100
output:
  validated_events_path: {tmp_path / "validated.jsonl"}
  summary_path: {tmp_path / "summary.json"}
  run_result_path: {tmp_path / "result.json"}
""",
        encoding="utf-8",
    )
    return config_path


def _interaction_event(query_id: str, trace_id: str, ts: str, latency_ms: int) -> dict[str, object]:
    return {
        "query_id": query_id,
        "trace_id": trace_id,
        "request_timestamp": ts,
        "response_timestamp": ts,
        "prompt_text": "prompt",
        "response_text": "response",
        "model_context": {
            "query_id": query_id,
            "trace_id": trace_id,
            "model_version": "m-v",
            "dataset_version": None,
            "provider": "prov",
            "model_name": "name",
        },
        "token_usage": {
            "query_id": query_id,
            "trace_id": trace_id,
            "model_version": "m-v",
            "dataset_version": None,
            "input_tokens": 1,
            "output_tokens": 1,
            "recorded_at": ts,
        },
        "latency": {
            "query_id": query_id,
            "trace_id": trace_id,
            "request_timestamp": ts,
            "response_timestamp": ts,
            "latency_ms": latency_ms,
        },
        "retrieval_references": [],
    }


def _retrieval_event(query_id: str, trace_id: str, ts: str) -> dict[str, object]:
    return {
        "query_id": query_id,
        "trace_id": trace_id,
        "retrieval_timestamp": ts,
        "query_text": "hello",
        "retrieval_system": "r",
        "top_k": 1,
        "references": [],
    }


def test_cli_schema_and_time_filter(repo_root: Path, tmp_path: Path) -> None:
    interactions_path = tmp_path / "interactions.jsonl"
    retrievals_path = tmp_path / "retrievals.jsonl"

    old = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC).isoformat()
    new = datetime.datetime(2026, 2, 1, tzinfo=datetime.UTC).isoformat()

    interactions = [
        _interaction_event("q-old", "t-old", old, 10),
        _interaction_event("q-new", "t-new", new, 20),
    ]
    retrievals = [
        _retrieval_event("q-old-r", "t-old-r", old),
        _retrieval_event("q-new-r", "t-new-r", new),
    ]

    interactions_path.write_text("\n".join(json.dumps(item) for item in interactions) + "\n", encoding="utf-8")
    retrievals_path.write_text("\n".join(json.dumps(item) for item in retrievals) + "\n", encoding="utf-8")

    config_path = _write_obs_config(tmp_path, interactions_path, retrievals_path)

    result = _run_cli(
        [
            "--config",
            str(config_path),
            "--schema",
            "--start-time",
            "2026-01-15T00:00:00+00:00",
            "--end-time",
            "2026-02-15T00:00:00+00:00",
        ],
        repo_root,
    )

    assert result.returncode == 0
    assert "Detected schema for interaction events:" in result.stdout

    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert summary["interactions_loaded"] == 1
    assert summary["retrievals_loaded"] == 1


def test_cli_export_csv(repo_root: Path, tmp_path: Path) -> None:
    interactions_path = tmp_path / "interactions.jsonl"
    retrievals_path = tmp_path / "retrievals.jsonl"
    ts = datetime.datetime(2026, 3, 1, tzinfo=datetime.UTC).isoformat()

    interactions_path.write_text(json.dumps(_interaction_event("q1", "t1", ts, 12)) + "\n", encoding="utf-8")
    retrievals_path.write_text(json.dumps(_retrieval_event("q2", "t2", ts)) + "\n", encoding="utf-8")

    config_path = _write_obs_config(tmp_path, interactions_path, retrievals_path)
    export_base = tmp_path / "events.csv"

    result = _run_cli(["--config", str(config_path), "--export-csv", str(export_base)], repo_root)

    assert result.returncode == 0
    assert (tmp_path / "events_interactions.csv").exists()
    assert (tmp_path / "events_retrievals.csv").exists()


@pytest.mark.skipif(__import__("importlib").util.find_spec("pyarrow") is None, reason="pyarrow not installed")
def test_cli_export_parquet(repo_root: Path, tmp_path: Path) -> None:
    interactions_path = tmp_path / "interactions.jsonl"
    retrievals_path = tmp_path / "retrievals.jsonl"
    ts = datetime.datetime(2026, 3, 1, tzinfo=datetime.UTC).isoformat()

    interactions_path.write_text(json.dumps(_interaction_event("q1", "t1", ts, 12)) + "\n", encoding="utf-8")
    retrievals_path.write_text(json.dumps(_retrieval_event("q2", "t2", ts)) + "\n", encoding="utf-8")

    config_path = _write_obs_config(tmp_path, interactions_path, retrievals_path)
    export_base = tmp_path / "events.parquet"

    result = _run_cli(["--config", str(config_path), "--export-parquet", str(export_base)], repo_root)

    assert result.returncode == 0
    assert (tmp_path / "events_interactions.parquet").exists()
    assert (tmp_path / "events_retrievals.parquet").exists()


def test_cli_detect_anomalies(repo_root: Path, tmp_path: Path) -> None:
    interactions_path = tmp_path / "interactions.jsonl"
    retrievals_path = tmp_path / "retrievals.jsonl"
    ts = datetime.datetime(2026, 4, 1, tzinfo=datetime.UTC).isoformat()

    interactions = [_interaction_event(f"q{i}", f"t{i}", ts, 10) for i in range(10)]
    interactions.append(_interaction_event("q-outlier", "t-outlier", ts, 1000))
    retrievals = [_retrieval_event("q-r", "t-r", ts)]

    interactions_path.write_text("\n".join(json.dumps(item) for item in interactions) + "\n", encoding="utf-8")
    retrievals_path.write_text("\n".join(json.dumps(item) for item in retrievals) + "\n", encoding="utf-8")

    config_path = _write_obs_config(tmp_path, interactions_path, retrievals_path)
    result = _run_cli(["--config", str(config_path), "--detect-anomalies"], repo_root)

    assert result.returncode == 0
    assert "Anomalies in interaction events:" in result.stdout
    assert "outlier latency_ms=1000" in result.stdout


def test_validate_config_subcommand(repo_root: Path, tmp_path: Path) -> None:
    config_path = tmp_path / "valid.yaml"
    config_path.write_text(
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

    result = _run_cli(["validate-config", str(config_path)], repo_root)
    assert result.returncode == 0
    assert "is valid" in result.stdout


def test_validate_config_subcommand_invalid(repo_root: Path, tmp_path: Path) -> None:
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(
        """
events:
  interactions_path: interactions.jsonl
output:
  summary_path: summary.json
""",
        encoding="utf-8",
    )

    result = _run_cli(["validate-config", str(config_path)], repo_root)
    assert result.returncode == 1
    assert "is INVALID" in result.stdout


def test_diff_contracts_subcommand_breaking_change(repo_root: Path, tmp_path: Path) -> None:
    old_path = tmp_path / "old.json"
    new_path = tmp_path / "new.json"

    old_path.write_text(json.dumps({"field": "value", "count": 1}), encoding="utf-8")
    new_path.write_text(json.dumps({"field": "value", "count": "one"}), encoding="utf-8")

    result = _run_cli(["diff-contracts", str(old_path), str(new_path)], repo_root)
    assert result.returncode == 1
    assert "Breaking changes detected" in result.stdout


def test_diff_contracts_subcommand_missing_args(repo_root: Path) -> None:
    result = _run_cli(["diff-contracts"], repo_root)
    assert result.returncode == 2
    assert "Usage: python -m llm_observability_analytics.cli.main diff-contracts" in result.stdout


def test_visualize_pipeline_subcommand(repo_root: Path, tmp_path: Path) -> None:
    interactions = tmp_path / "interactions.jsonl"
    retrievals = tmp_path / "retrievals.jsonl"
    config_path = _write_obs_config(tmp_path, interactions, retrievals)

    result = _run_cli(["visualize-pipeline", str(config_path)], repo_root)
    assert result.returncode == 0
    assert "graph TD" in result.stdout


def test_cli_invalid_start_time_returns_error(repo_root: Path, tmp_path: Path) -> None:
    interactions_path = tmp_path / "interactions.jsonl"
    retrievals_path = tmp_path / "retrievals.jsonl"
    ts = datetime.datetime(2026, 4, 1, tzinfo=datetime.UTC).isoformat()
    interactions_path.write_text(json.dumps(_interaction_event("q1", "t1", ts, 10)) + "\n", encoding="utf-8")
    retrievals_path.write_text(json.dumps(_retrieval_event("q2", "t2", ts)) + "\n", encoding="utf-8")
    config_path = _write_obs_config(tmp_path, interactions_path, retrievals_path)

    result = _run_cli(["--config", str(config_path), "--start-time", "not-a-time"], repo_root)
    assert result.returncode != 0


def test_coverage_report_subcommand_unit(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    class _Result:
        returncode = 0
        stdout = "ok"

    def _fake_run(*args: object, **kwargs: object) -> _Result:
        return _Result()

    monkeypatch.setattr(cli_main.subprocess, "run", _fake_run)
    code = cli_main.coverage_report_cmd()

    captured = capsys.readouterr()
    assert code == 0
    assert "Running pytest with coverage" in captured.out
    assert "All tests passed." in captured.out
