import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_summary(tmp_path):
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
    # Write two valid interaction events with different latencies
    import copy
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)
    event1 = {
        "query_id": "q1",
        "trace_id": "t1",
        "request_timestamp": now.isoformat(),
        "response_timestamp": (now + datetime.timedelta(milliseconds=100)).isoformat(),
        "prompt_text": "prompt1",
        "response_text": "response1",
        "model_context": {
            "query_id": "q1",
            "trace_id": "t1",
            "model_version": "m-v",
            "dataset_version": "v1",
            "provider": "prov",
            "model_name": "name",
            "contract_version": "1.0",
        },
        "token_usage": {
            "query_id": "q1",
            "trace_id": "t1",
            "model_version": "m-v",
            "dataset_version": "v1",
            "input_tokens": 1,
            "output_tokens": 1,
            "recorded_at": now.isoformat(),
            "contract_version": "1.0",
        },
        "latency": {
            "query_id": "q1",
            "trace_id": "t1",
            "request_timestamp": now.isoformat(),
            "response_timestamp": (now + datetime.timedelta(milliseconds=100)).isoformat(),
            "latency_ms": 100,
            "contract_version": "1.0",
        },
        "retrieval_references": [],
    }
    event2 = copy.deepcopy(event1)
    event2["query_id"] = "q2"
    event2["trace_id"] = "t2"
    event2["prompt_text"] = "prompt2"
    event2["response_text"] = "response2"
    event2["latency"]["latency_ms"] = 200
    event2["latency"]["query_id"] = "q2"
    event2["latency"]["trace_id"] = "t2"
    event2["model_context"]["query_id"] = "q2"
    event2["model_context"]["trace_id"] = "t2"
    event2["token_usage"]["query_id"] = "q2"
    event2["token_usage"]["trace_id"] = "t2"
    event2["request_timestamp"] = now.isoformat()
    event2["response_timestamp"] = (now + datetime.timedelta(milliseconds=200)).isoformat()
    interactions_path.write_text(
        json.dumps(event1) + "\n" + json.dumps(event2) + "\n", encoding="utf-8"
    )
    retrievals_path.write_text("", encoding="utf-8")
    env = dict(**os.environ)
    env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_observability_analytics.cli.main",
            "--config",
            str(config_path),
            "--summary",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    # Check output contains summary lines
    assert "Event Summary Report:" in result.stdout
    assert "Interactions loaded: 2" in result.stdout
    assert "Interaction latency (ms): min=100, max=200, avg=150.00" in result.stdout
    # Check summary JSON file
    with summary_path.open("r", encoding="utf-8") as f:
        summary = json.load(f)
    assert summary["interactions_loaded"] == 2
    assert summary["interaction_latency_min_ms"] == 100
    assert summary["interaction_latency_max_ms"] == 200
    assert summary["interaction_latency_avg_ms"] == 150.0
    assert summary["interaction_latency_avg_ms"] == 150.0
    assert summary["interaction_latency_avg_ms"] == 150.0
