import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_help():
    env = dict(**os.environ)
    env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")
    result = subprocess.run(
        [sys.executable, "-m", "llm_observability_analytics.cli.main", "--help"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
    assert "--config" in result.stdout
    assert "--dry-run" in result.stdout


def test_cli_dry_run(tmp_path):
    config_path = tmp_path / "config.yaml"
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
    env = dict(**os.environ)
    env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_observability_analytics.cli.main",
            "--config",
            str(config_path),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "Dry run successful" in result.stdout


def test_cli_event_processing(tmp_path):
    # Prepare minimal config and input files
    config_path = tmp_path / "config.yaml"
    interactions_path = tmp_path / "interactions.jsonl"
    retrievals_path = tmp_path / "retrievals.jsonl"
    summary_path = tmp_path / "summary.json"
    config_path.write_text(
        f"""
events:
  interactions_path: {interactions_path.as_posix()}
  retrievals_path: {retrievals_path.as_posix()}
  max_events: 10
output:
  validated_events_path: {tmp_path / "validated.jsonl"}
  summary_path: {summary_path.as_posix()}
  run_result_path: {tmp_path / "result.json"}
""",
        encoding="utf-8",
    )
    # Write minimal valid interaction and retrieval event
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    interaction_event = {
        "query_id": "q1",
        "trace_id": "t1",
        "request_timestamp": now,
        "response_timestamp": now,
        "prompt_text": "prompt",
        "response_text": "response",
        "model_context": {
            "query_id": "q1",
            "trace_id": "t1",
            "model_version": "m-v",
            "dataset_version": None,
            "provider": "prov",
            "model_name": "name",
        },
        "token_usage": {
            "query_id": "q1",
            "trace_id": "t1",
            "model_version": "m-v",
            "dataset_version": None,
            "input_tokens": 1,
            "output_tokens": 1,
            "recorded_at": now,
        },
        "latency": {
            "query_id": "q1",
            "trace_id": "t1",
            "request_timestamp": now,
            "response_timestamp": now,
            "latency_ms": 1,
        },
        "retrieval_references": [],
    }
    retrieval_event = {
        "query_id": "q2",
        "trace_id": "t2",
        "retrieval_timestamp": now,
        "query_text": "hello",
        "retrieval_system": "r",
        "top_k": 1,
        "references": [],
    }
    interactions_path.write_text(json.dumps(interaction_event) + "\n", encoding="utf-8")
    retrievals_path.write_text(json.dumps(retrieval_event) + "\n", encoding="utf-8")
    env = dict(**os.environ)
    env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_observability_analytics.cli.main",
            "--config",
            str(config_path),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "Event processing complete" in result.stdout
    assert summary_path.exists()
    with summary_path.open("r", encoding="utf-8") as f:
        summary = json.load(f)
    assert summary["interactions_loaded"] == 1
    assert summary["retrievals_loaded"] == 1
    assert summary["retrievals_loaded"] == 1
    assert summary["retrievals_loaded"] == 1
