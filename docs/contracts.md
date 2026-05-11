# Contracts Overview

The canonical schema reference is [`data-contracts.md`](data-contracts.md). This document is the index of what each package produces and consumes inside the monorepo, and how those handoffs stay aligned with sibling repositories that previously shipped these packages independently.

## Handoffs at a glance

| Producer | Artifact | Consumer |
| --- | --- | --- |
| `llm_knowledge_ingestion` | `documents.jsonl`, `chunks.jsonl`, `lineage.jsonl`, `index_records.jsonl` | `llm_dataset_foundry`, runtime serving |
| `llm_observability_analytics` | `interactions.jsonl`, `retrieval_traces.jsonl` | `llm_dataset_foundry` |
| `llm_dataset_foundry` | `prompt_response.jsonl`, `retrieval_evaluation.jsonl`, `split_assignments.jsonl`, `dataset_manifest.json`, `dataset_version_metadata.json`, `quality_report.json` | training and evaluation systems |

## Shared identifier policy

Every handoff must preserve these identifiers when present:

- `source_id`
- `document_id`
- `chunk_id`
- `query_id`
- `trace_id`
- `dataset_id`
- `dataset_version`
- `model_version`

Field naming is snake_case across all packages and artifact files.

## Machine-readable summary

[`shared-contract-summary.json`](shared-contract-summary.json) encodes identifiers, contract versions, and required handoff fields. It is the source of truth for [`scripts/validate_shared_contracts.py`](../scripts/validate_shared_contracts.py) and for cross-repo alignment checks against sibling repositories.

## Updating contracts

See [`contract-consistency.md`](contract-consistency.md) for the safe-update workflow.
