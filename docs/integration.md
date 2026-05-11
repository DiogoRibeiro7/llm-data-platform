# Integration

How the three packages compose end-to-end. The flow is one-directional and entirely file-based: each stage reads JSONL produced by the previous stage and writes JSONL plus a summary/manifest.

## End-to-end flow

```text
source files
    │
    ▼
llm_knowledge_ingestion
    │   documents.jsonl    (document_id, content_hash, source_id)
    │   chunks.jsonl       (chunk_id, document_id, text)
    │   lineage.jsonl      (chunk → document references)
    │   index_records.jsonl
    │
    ├──────────────────────────────────────────────┐
    │                                              │
    ▼                                              ▼
runtime serving                              llm_dataset_foundry
    │  (uses chunk_id when surfacing context)      ▲
    ▼                                              │
llm_observability_analytics                        │
    │   interactions.jsonl  (query_id, trace_id,   │
    │                        prompt_text,          │
    │                        response_text,        │
    │                        retrieval_references) │
    │   retrieval_traces.jsonl (query_id,          │
    │                           trace_id,          │
    │                           references[])      │
    └──────────────────────────────────────────────┘
                                                   │
                                                   ▼
                                        prompt_response.jsonl
                                        retrieval_evaluation.jsonl
                                        split_assignments.jsonl
                                        dataset_manifest.json
                                        quality_report.json
```

## Handoff artifacts

### Ingestion → Foundry

- `documents.jsonl` — normalized document records keyed by `document_id`.
- `chunks.jsonl` — chunks keyed by `chunk_id`, each carrying `document_id`.
- `lineage.jsonl` — chunk-to-document lineage.

### Ingestion → Observability (at runtime)

- `chunks.jsonl` — runtime systems index and retrieve from these chunks; surface `chunk_id` and `document_id` in retrieval results so observability can correlate.

### Observability → Foundry

- `interactions.jsonl` — one record per LLM interaction with `query_id`, `trace_id`, `prompt_text`, `response_text`, `model_context`, `retrieval_references`, `feedback`.
- `retrieval_traces.jsonl` — one record per retrieval call with `query_id`, `trace_id`, `references[]` (each carrying `document_id`, `chunk_id`, `rank`, `score`), `model_version`, `dataset_version`.

### Foundry outputs

- `prompt_response.jsonl` — curated training pairs.
- `retrieval_evaluation.jsonl` — retrieval-eval records with ground-truth alignment.
- `split_assignments.jsonl` — deterministic train/validation/test assignment.
- `dataset_manifest.json` and `dataset_version_metadata.json` — manifest plus version metadata.
- `quality_report.json` — quality and dedup stats.

## Shared identifier policy

All handoff artifacts must preserve, when available:

- `source_id` — upstream knowledge source.
- `document_id` — normalized document.
- `chunk_id` — chunk derived from a document.
- `query_id` — a single user/system query.
- `trace_id` — execution trace grouping events/spans.
- `dataset_id`, `dataset_version` — curated dataset identity.
- `model_version` — model that produced runtime output.

Snake_case naming, stable across packages.

## Example artifacts

See [`examples/integration/`](../examples/integration/) for sample JSONL handoff files matching each step above.

## End-to-end test

[`tests/test_end_to_end_pipeline.py`](../tests/test_end_to_end_pipeline.py) wires up the three CLIs in sequence with temporary configs and verifies the expected artifacts appear. Use it as a reference for working config shapes.
