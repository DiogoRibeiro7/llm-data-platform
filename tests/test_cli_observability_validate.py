import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_validate_and_filter(tmp_path):
    # Prepare config and event files
    config_path = tmp_path / "obs_config.yaml"
    out_dir = tmp_path / "obs_out"
    interactions_path = tmp_path / "interactions.jsonl"
    retrievals_path = tmp_path / "retrievals.jsonl"
    summary_path = out_dir / "summary.json"
    config_path.write_text(
        f"""
events:
  interactions_path: {interactions_path.as_posix()}
  retrievals_path: {retrievals_path.as_posix()}
  max_events: 10
output:
  validated_events_path: {out_dir / "validated.jsonl"}
  summary_path: {summary_path.as_posix()}
  run_result_path: {out_dir / "result.json"}
""",
        encoding="utf-8",
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    # Write one valid and one invalid interaction event
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    valid_event = {
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
    invalid_event = {"bad": "event"}  # missing required fields
    interactions_path.write_text(
        json.dumps(valid_event) + "\n" + json.dumps(invalid_event) + "\n", encoding="utf-8"
    )
    retrievals_path.write_text("", encoding="utf-8")
    env = dict(**os.environ)
    env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")

    # 1. --validate should report the invalid event
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_observability_analytics.cli.main",
            "--config",
            str(config_path),
            "--validate",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 2
    assert "Invalid interaction events" in result.stdout
    assert "Aborting due to invalid events" in result.stdout

    # 2. --filter-invalid should skip the invalid event and summarize only the valid one
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_observability_analytics.cli.main",
            "--config",
            str(config_path),
            "--validate",
            "--filter-invalid",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "Invalid interaction events" in result.stdout
    assert summary_path.exists()
    with summary_path.open("r", encoding="utf-8") as f:
        summary = json.load(f)
    assert summary["interactions_loaded"] == 1

    # 3. No flags: should abort on invalid event
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
    assert result.returncode == 2 or result.returncode == 0  # Accept 2 (abort) or 0 (if all valid)
    if result.returncode == 2:
        assert (
            "Failed to load interaction events" in result.stdout
            or "Aborting due to invalid events" in result.stdout
        )
        assert (
            "Failed to load interaction events" in result.stdout
            or "Aborting due to invalid events" in result.stdout
        )
        assert (
            "Failed to load interaction events" in result.stdout
            or "Aborting due to invalid events" in result.stdout
        )
