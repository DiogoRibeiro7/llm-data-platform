# Ingestion Pipeline

The knowledge ingestion pipeline reads local source files, normalizes them into canonical documents, deduplicates by content hash, splits documents into token-budgeted chunks, and writes index-ready artifacts.

## Run

Install (from the repo root):

```bash
pip install -e ".[dev]"
```

Dry run (validates config and lists planned input files without writing artifacts):

```bash
python -m llm_knowledge_ingestion.cli.main --dry-run
```

Execute (uses [`configs/ingestion.yaml`](../configs/ingestion.yaml) by default):

```bash
python -m llm_knowledge_ingestion.cli.main
# or with a custom config
python -m llm_knowledge_ingestion.cli.main --config path/to/ingest.yaml
```

## Config shape

```yaml
ingestion:
  source_id: my-source           # stable identifier, non-empty
  input_path: ./examples         # directory scanned recursively
  max_documents: 100             # cap on processed files
chunking:
  strategy: fixed_tokens
  target_tokens: 400
  overlap_tokens: 40
output:
  normalized_documents_path: ./out/documents
  chunks_path: ./out/chunks
  lineage_path: ./out/lineage
  index_records_path: ./out/index
  run_result_path: ./out/run/ingestion_result.json
```

Relative paths are resolved against the config file's directory.

## Supported inputs

- `.txt`
- `.md`
- `.json`

Files are discovered recursively under `ingestion.input_path` and processed in stable sorted order.

## Outputs

- `<normalized_documents_path>/documents.jsonl` — one normalized document per line.
- `<chunks_path>/chunks.jsonl` — one chunk per line, each carrying `document_id`.
- `<lineage_path>/lineage.jsonl` — one lineage reference per chunk.
- `<index_records_path>/index_records.jsonl` — one index-ready record per chunk.
- `<run_result_path>` — JSON summary with counters and warnings.

All JSON output is deterministic at the field level (`sort_keys=True`) so artifacts are diffable across runs.

## Example

A worked config is constructed at runtime in [`tests/test_end_to_end_pipeline.py`](../tests/test_end_to_end_pipeline.py) and sample inputs live under [`examples/`](../examples/).
