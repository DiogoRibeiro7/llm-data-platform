# Architecture

This monorepo packages three cooperating Python libraries that cover the LLM data lifecycle: knowledge ingestion, runtime observability, and dataset curation. Each package owns one stage and exchanges JSONL artifacts keyed by shared contract identifiers.

## Stages

### `llm_knowledge_ingestion`

Owns transforming raw source files into normalized, chunked, index-ready records.

Modules:

- `io/` — local file discovery and reading.
- `parsers/` — format-specific text extraction (`.txt`, `.md`, `.json`).
- `normalize/` — canonical document model with deterministic content hashing.
- `chunking/` — token-budgeted chunk splitting with overlap.
- `dedup/` — content-hash deduplication.
- `contracts/` — shared entity definitions.
- `pipeline/` — config loader and orchestrator.
- `cli/` — `llm-knowledge-ingest` entrypoint.

### `llm_observability_analytics`

Owns runtime telemetry standardization and analytics-ready event modeling for retrieval and LLM interactions.

Modules:

- `events/` — interaction and retrieval-trace event envelopes plus loaders with validation.
- `traces/` — trace grouping and span correlation.
- `metrics/` — derived KPI and aggregation models.
- `storage/` — persistence adapters.
- `reports/` — report assembly contracts.
- `contracts/` — shared identifiers and contract version constants.
- `pipeline/` — config loader.
- `cli/` — `llm-observability` entrypoint with summary, schema, validation, anomaly detection, CSV/Parquet export, plus `validate-config`, `diff-contracts`, `visualize-pipeline`, `coverage-report` subcommands.

### `llm_dataset_foundry`

Owns curated dataset construction from ingestion artifacts and runtime traces.

Modules:

- `ingest/` — loaders for normalized documents and trace events.
- `quality/` — text quality and dedup checks.
- `splits/` — deterministic train/validation/test assignment.
- `versioning/` — dataset manifest and version metadata.
- `reports/` — quality report assembly.
- `contracts/` — dataset-side contract entities.
- `pipeline/` — config loader and orchestrator.
- `cli/` — `llm-dataset-foundry` entrypoint.

## Shared invariants

- **Identifiers are stable across stages.** `source_id`, `document_id`, `chunk_id`, `query_id`, `trace_id`, `dataset_id`, `dataset_version`, `model_version` are produced once and preserved through every downstream artifact.
- **JSONL is the handoff format.** One record per line, snake_case fields, deterministic key ordering (`sort_keys=True`) so artifacts are diffable and reproducible.
- **Append-friendly storage.** Each stage writes new artifacts rather than mutating prior ones, so reruns are idempotent and lineage is auditable.
- **Schema evolution discipline.** Contract versions are explicit constants; breaking changes go through the `diff-contracts` workflow before merging.

## Non-functional goals

- Deterministic identity for documents, chunks, and traces.
- Low-friction integration with existing monitoring and storage systems through file-based interfaces.
- Strict typing (`mypy --strict`) and high test coverage gates.
- Per-package CLIs that run in isolation but compose via shared on-disk contracts.
