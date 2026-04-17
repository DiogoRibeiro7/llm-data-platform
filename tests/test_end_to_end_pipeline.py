import json
import os
import subprocess
import sys
from pathlib import Path


def test_end_to_end_pipeline(tmp_path):
    """
    Runs the ingestion, dataset curation, and observability analytics CLIs in sequence
    using sample data, and verifies that all expected output artifacts are produced.
    """
    # 1. Prepare input directories and files
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "doc1.txt").write_text("Sample document for ingestion.", encoding="utf-8")

    # 2. Ingestion config
    ingestion_config = tmp_path / "ingest_config.yaml"
    ingest_out = tmp_path / "ingest_out"
    ingestion_config.write_text(
        f"""
ingestion:
  source_id: test-source
  input_path: {input_dir.as_posix()}
  max_documents: 1
chunking:
  strategy: fixed_tokens
  target_tokens: 5
  overlap_tokens: 1
output:
  normalized_documents_path: {ingest_out / "documents"}
  chunks_path: {ingest_out / "chunks"}
  lineage_path: {ingest_out / "lineage"}
  index_records_path: {ingest_out / "index"}
  run_result_path: {ingest_out / "run" / "ingestion_result.json"}
""",
        encoding="utf-8",
    )

    # 3. Run ingestion CLI
    env = dict(**os.environ)
    env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "llm_knowledge_ingestion.cli.main",
            "--config",
            str(ingestion_config),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "Ingestion completed" in result.stdout
    assert (ingest_out / "documents" / "documents.jsonl").exists()

    # 4. Dataset curation config
    foundry_config = tmp_path / "foundry_config.yaml"
    foundry_out = tmp_path / "foundry_out"
    foundry_config.write_text(
        f"""
ingest:
  normalized_documents_file: {ingest_out / "documents" / "documents.jsonl"}
  interaction_events_file: {tmp_path / "dummy_interactions.jsonl"}
  retrieval_events_file: {tmp_path / "dummy_retrievals.jsonl"}
  max_records: 1
dataset:
  dataset_name: test-ds
  dataset_id: ds-1
  dataset_version: v1
  schema_version: 1.0
  model_version: m-v
quality:
  dedup_enabled: true
  min_text_length: 1
splits:
  seed: 42
  train_ratio: 0.8
  validation_ratio: 0.1
  test_ratio: 0.1
output:
  curated_dataset_path: {foundry_out / "curated"}
  reports_path: {foundry_out / "reports"}
  manifests_path: {foundry_out / "manifests"}
""",
        encoding="utf-8",
    )
    # Write dummy events for foundry
    (tmp_path / "dummy_interactions.jsonl").write_text("", encoding="utf-8")
    (tmp_path / "dummy_retrievals.jsonl").write_text("", encoding="utf-8")

    # 5. Run dataset foundry CLI
    result = subprocess.run(
        [sys.executable, "-m", "llm_dataset_foundry.cli.main", "--config", str(foundry_config)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "Dataset build completed" in result.stdout
    assert (foundry_out / "curated" / "prompt_response.jsonl").exists()

    # 6. Observability analytics config
    obs_config = tmp_path / "obs_config.yaml"
    obs_out = tmp_path / "obs_out"
    obs_config.write_text(
        f"""
events:
  interactions_path: {tmp_path / "dummy_interactions.jsonl"}
  retrievals_path: {tmp_path / "dummy_retrievals.jsonl"}
  max_events: 1
output:
  validated_events_path: {obs_out / "validated.jsonl"}
  summary_path: {obs_out / "summary.json"}
  run_result_path: {obs_out / "result.json"}
""",
        encoding="utf-8",
    )

    # 7. Run observability analytics CLI
    result = subprocess.run(
        [sys.executable, "-m", "llm_observability_analytics.cli.main", "--config", str(obs_config)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "Event processing complete" in result.stdout
    assert (obs_out / "summary.json").exists()
    with (obs_out / "summary.json").open("r", encoding="utf-8") as f:
        summary = json.load(f)
    assert "interactions_loaded" in summary
    assert "retrievals_loaded" in summary
    assert "retrievals_loaded" in summary
    assert "retrievals_loaded" in summary
