# Integration Examples

Paired JSONL files showing each handoff between the three packages. Use them as fixtures or as references for the exact field set required at each boundary. See [docs/integration.md](../../docs/integration.md) and [docs/data-contracts.md](../../docs/data-contracts.md) for the contract.

## Ingestion → Observability and Foundry

- `ingestion_documents_for_dataset_foundry.jsonl` — normalized documents emitted by ingestion.
- `ingestion_chunks_for_observability.jsonl` — chunks that runtime serving indexes and that observability references by `chunk_id` / `document_id`.
- `ingestion_lineage_for_dataset_foundry.jsonl` — chunk-to-document lineage consumed by the foundry.

## Observability → Foundry

- `output_for_dataset_foundry_interactions.jsonl` — interaction events with `query_id`, `trace_id`, `prompt_text`, `response_text`, `model_context`, `retrieval_references`.
- `output_for_dataset_foundry_retrieval_traces.jsonl` — retrieval traces with `query_id`, `trace_id`, `references[]`, `model_version`, `dataset_version`.

## Foundry outputs

- `output_prompt_response_sample.jsonl` — curated prompt-response pairs.
- `output_retrieval_eval_sample.jsonl` — curated retrieval-evaluation records.
- `output_manifest_sample.json` — dataset manifest.

## "Input from" mirrors

- `input_from_ingestion_documents.jsonl`, `input_from_ingestion_chunks.jsonl` — the same ingestion outputs framed as foundry/observability inputs.
- `input_from_observability_interactions.jsonl`, `input_from_observability_retrieval_traces.jsonl` — the observability outputs framed as foundry inputs.

These mirror pairs exist so each consumer can be tested in isolation against the exact shape it will see at runtime.
