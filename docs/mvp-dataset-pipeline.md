# Dataset Pipeline

The dataset foundry pipeline loads normalized documents plus interaction and retrieval-trace events, builds curated prompt-response and retrieval-evaluation datasets, runs quality checks, assigns deterministic train/validation/test splits, and writes manifests plus a quality report.

## Run

```bash
pip install -e ".[dev]"
```

Dry run (validates config and module wiring):

```bash
python -m llm_dataset_foundry.cli.main --dry-run
```

Execute (uses [`configs/foundry.yaml`](../configs/foundry.yaml) by default):

```bash
python -m llm_dataset_foundry.cli.main
# or with a custom config
python -m llm_dataset_foundry.cli.main --config path/to/foundry.yaml
```

## Config shape

```yaml
ingest:
  normalized_documents_file: ./ingest_out/documents/documents.jsonl
  interaction_events_file: ./obs_out/interactions.jsonl
  retrieval_events_file: ./obs_out/retrieval_traces.jsonl
  max_records: 10000
dataset:
  dataset_name: my-dataset
  dataset_id: ds-1
  dataset_version: v1
  schema_version: "1.0"
  model_version: my-model-v1
quality:
  dedup_enabled: true
  min_text_length: 10
splits:
  seed: 42
  train_ratio: 0.8
  validation_ratio: 0.1
  test_ratio: 0.1                 # ratios must sum to 1.0
output:
  curated_dataset_path: ./out/curated
  reports_path: ./out/reports
  manifests_path: ./out/manifests
```

Relative paths resolve against the config file's directory.

## Inputs

JSONL files (one JSON object per line):

- `ingest.normalized_documents_file` — `documents.jsonl` produced by ingestion.
- `ingest.interaction_events_file` — `interactions.jsonl` produced by observability.
- `ingest.retrieval_events_file` — `retrieval_traces.jsonl` produced by observability.

## Outputs

- `<curated_dataset_path>/prompt_response.jsonl`
- `<curated_dataset_path>/retrieval_evaluation.jsonl`
- `<curated_dataset_path>/split_assignments.jsonl`
- `<reports_path>/quality_report.json`
- `<manifests_path>/dataset_manifest.json`
- `<manifests_path>/dataset_version_metadata.json`

See [`data-contracts.md`](data-contracts.md) for field-level schemas and [`tests/test_end_to_end_pipeline.py`](../tests/test_end_to_end_pipeline.py) for a runnable example.
