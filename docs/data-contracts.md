# Data Contracts

Canonical schemas for the artifacts exchanged between packages. All record formats are JSONL with snake_case fields and deterministic key ordering.

## Shared platform identifiers

- `source_id` — upstream knowledge source.
- `document_id` — normalized document.
- `chunk_id` — chunk derived from a document.
- `query_id` — a single user or system query.
- `trace_id` — execution trace grouping events and spans.
- `dataset_id` — curated dataset identity.
- `dataset_version` — immutable snapshot version of a dataset.
- `model_version` — model used to produce runtime outputs.

Contract version constants:

- `OBSERVABILITY_CONTRACT_VERSION = "1.0"`

## Ingestion artifacts (produced by `llm_knowledge_ingestion`)

### `documents.jsonl`

One normalized document per line.

Core fields: `document_id`, `source_id`, `content_hash`, `text`, `metadata`.

### `chunks.jsonl`

One chunk per line.

Core fields: `chunk_id`, `document_id`, `text`, `token_count`, ordering fields for chunk index within document.

### `lineage.jsonl`

Chunk-to-document lineage references.

### `index_records.jsonl`

Index-ready records: `chunk_id`, `document_id`, `text`, and any embedding-ready metadata.

## Observability artifacts (produced by `llm_observability_analytics`)

### `LLMInteractionEvent` / `interactions.jsonl`

Core fields:

- `query_id`
- `trace_id`
- `request_timestamp`
- `response_timestamp`
- `prompt_text`
- `response_text`
- `model_context`
- `token_usage` (`input_tokens`, `output_tokens`, `total_tokens`, `model_version`)
- `latency` (`latency_ms`)
- `retrieval_references`
- `feedback`
- `contract_version`

### `RetrievalTraceEvent` / `retrieval_traces.jsonl`

Core fields:

- `query_id`
- `trace_id`
- `retrieval_timestamp`
- `query_text`
- `retrieval_system`
- `top_k`
- `references[]` (each with `document_id`, `chunk_id`, `rank`, `score`)
- `model_version`
- `dataset_version`
- `status`
- `contract_version`

### `UserFeedbackEvent`

Core fields: `query_id`, `trace_id`, `feedback_timestamp`, `rating`, `feedback_text`, `feedback_label`, optional `model_version`, `dataset_version`.

## Dataset artifacts (produced by `llm_dataset_foundry`)

### `prompt_response.jsonl`

Curated training pairs derived from interactions.

Core fields: `dataset_id`, `dataset_version`, `query_id`, `trace_id`, `prompt_text`, `response_text`, `model_version`, quality flags.

### `retrieval_evaluation.jsonl`

Retrieval-eval records with reference targets.

Core fields: `dataset_id`, `dataset_version`, `query_id`, `trace_id`, `references[]`, expected targets.

### `split_assignments.jsonl`

Deterministic train/validation/test assignment by `query_id`.

### `dataset_manifest.json` and `dataset_version_metadata.json`

Dataset identity, file inventory, schema version, model version, and provenance.

### `quality_report.json`

Aggregate dedup, length, and completeness statistics.

## Cross-repo linkage requirements

When producing handoff artifacts, always include:

- `query_id`
- `trace_id`
- `document_id` and `chunk_id` inside retrieval references
- `model_version`
- `dataset_version` when available
