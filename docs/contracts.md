# Contracts Overview

This repository uses the contract definitions in `docs/data-contracts.md` as the canonical schema reference.

## Cross-Repository Handoff Alignment

Incoming handoffs:

- from `llm-knowledge-ingestion`: `documents.jsonl`, `chunks.jsonl`
- from `llm-observability-analytics`: `interactions.jsonl`, `retrieval_traces.jsonl`

Outgoing artifacts:

- `prompt_response.jsonl`
- `retrieval_evaluation.jsonl`
- `split_assignments.jsonl`
- `dataset_manifest.json`
- `dataset_version_metadata.json`
- `quality_report.json`

## Shared Identifier Policy

All handoff artifacts must preserve these identifiers when available:

- `document_id`
- `chunk_id`
- `query_id`
- `trace_id`
- `dataset_id`
- `dataset_version`
- `model_version`

Field naming convention is snake_case across all repositories.
