# Examples

Sample inputs and reference handoff artifacts used by the three pipelines.

## Layout

- `sources/sample.txt`, `sources/sample.md`, `sources/sample.json` — small source documents for the ingestion pipeline. The default [`configs/ingestion.yaml`](../configs/ingestion.yaml) already points `ingestion.input_path` here.
- `normalized-documents/documents.jsonl` — example of ingestion output, ready to feed into `llm_dataset_foundry` via `ingest.normalized_documents_file`.
- `traces/interactions.jsonl`, `traces/retrieval.jsonl` — example runtime traces. Feed into the foundry as `interaction_events_file` / `retrieval_events_file`, or into observability as `events.interactions_path` / `events.retrievals_path`.
- `integration/` — paired input/output JSONL files demonstrating each handoff between packages. See [integration/README.md](integration/README.md).

## End-to-end example

[`tests/test_end_to_end_pipeline.py`](../tests/test_end_to_end_pipeline.py) wires up all three CLIs with sample data and verifies the expected artifacts. Use it as the working reference for config shapes and chained execution.
