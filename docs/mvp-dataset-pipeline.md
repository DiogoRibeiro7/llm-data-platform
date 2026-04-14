# MVP Dataset Pipeline

## Overview

The MVP pipeline loads local normalized documents and trace artifacts, builds prompt-response and retrieval-evaluation datasets, runs quality checks, assigns deterministic splits, and writes manifests/reports.

## Run

Install:

```bash
pip install -e .[dev]
```

Dry run:

```bash
python -m llm_dataset_foundry.cli.main --dry-run --config configs/base.yaml
```

Execute:

```bash
python -m llm_dataset_foundry.cli.main --config configs/base.yaml
```

## Inputs

Configured in `configs/base.yaml`:

- `ingest.normalized_documents_file`
- `ingest.interaction_events_file`
- `ingest.retrieval_events_file`

Input format is JSONL (one JSON object per line).

## Outputs

- `curated_dataset_path/prompt_response.jsonl`
- `curated_dataset_path/retrieval_evaluation.jsonl`
- `curated_dataset_path/split_assignments.jsonl`
- `reports_path/quality_report.json`
- `manifests_path/dataset_manifest.json`
- `manifests_path/dataset_version_metadata.json`
