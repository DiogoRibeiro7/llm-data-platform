# llm-data-platform

A Python monorepo for the LLM data lifecycle: ingest source documents into chunks, curate datasets from those chunks plus runtime traces, and observe LLM interactions with structured events and analytics.

The three packages share contract identifiers (`source_id`, `document_id`, `chunk_id`, `query_id`, `trace_id`, `dataset_id`, `dataset_version`, `model_version`) so artifacts produced by one stage flow cleanly into the next.

## Packages

| Package | Role | CLI module |
| --- | --- | --- |
| [`llm_knowledge_ingestion`](src/llm_knowledge_ingestion/) | Parses local files, normalizes them into documents, chunks them, and emits index-ready records with lineage. | `python -m llm_knowledge_ingestion.cli.main` |
| [`llm_dataset_foundry`](src/llm_dataset_foundry/) | Builds prompt–response and retrieval-evaluation datasets from normalized documents and trace artifacts, runs quality checks, assigns splits, writes manifests. | `python -m llm_dataset_foundry.cli.main` |
| [`llm_observability_analytics`](src/llm_observability_analytics/) | Loads runtime interaction and retrieval-trace events, validates them, computes summaries, detects anomalies, exports CSV/Parquet. | `python -m llm_observability_analytics.cli.main` (also installed as `llm-observability`) |

Data flow:

```text
sources ──▶ knowledge_ingestion ──▶ documents.jsonl, chunks.jsonl, lineage.jsonl
                                          │
                                          ▼
runtime ──▶ observability_analytics ──▶ interactions.jsonl, retrieval_traces.jsonl
                                          │
                                          ▼
                                   dataset_foundry ──▶ prompt_response.jsonl,
                                                       retrieval_evaluation.jsonl,
                                                       split_assignments.jsonl,
                                                       dataset_manifest.json
```

See [docs/architecture.md](docs/architecture.md) for boundaries and [docs/integration.md](docs/integration.md) for the full handoff contract.

## Install

Requires Python 3.12+.

```bash
python -m venv .venv
# Unix/macOS
source .venv/bin/activate
# Windows PowerShell
. .\.venv\Scripts\Activate.ps1

python -m pip install -U pip
pip install -e ".[dev]"
```

### Install profiles

| Extra | Adds | Needed for |
| --- | --- | --- |
| (base) | `PyYAML` | All three pipelines |
| `dev` | `ruff`, `mypy`, `pytest`, `pytest-cov` | Local development |
| `observability-cli` | `jsonschema`, `numpy`, `pandas` | `--validate`, `validate-config`, `--detect-anomalies`, `--export-csv` |
| `parquet` | `pyarrow` | `--export-parquet` (combine with `observability-cli`) |

Example: `pip install -e ".[dev,observability-cli,parquet]"`.

## Running the pipelines

Each pipeline takes a YAML config via `--config` (with a runnable default that points at the bundled examples) and supports `--dry-run` to validate wiring without writing artifacts. See the [docs/mvp-*.md](docs/) files for the required keys, and [tests/test_end_to_end_pipeline.py](tests/test_end_to_end_pipeline.py) for a fully worked example that runs all three end to end.

Per-pipeline default configs live in [configs/](configs/) and resolve their relative paths against the [examples/](examples/) directory, writing outputs to `artifacts/` (gitignored).

### Ingestion

```bash
python -m llm_knowledge_ingestion.cli.main                    # uses configs/ingestion.yaml
python -m llm_knowledge_ingestion.cli.main --config my.yaml   # or your own
```

Reads `.txt`, `.md`, `.json` from `ingestion.input_path` and writes `documents.jsonl`, `chunks.jsonl`, `lineage.jsonl`, `index_records.jsonl`. See [docs/mvp-ingestion.md](docs/mvp-ingestion.md).

### Dataset foundry

```bash
python -m llm_dataset_foundry.cli.main                        # uses configs/foundry.yaml
```

Reads normalized documents and trace JSONL, writes `prompt_response.jsonl`, `retrieval_evaluation.jsonl`, `split_assignments.jsonl`, plus a quality report and dataset manifest. See [docs/mvp-dataset-pipeline.md](docs/mvp-dataset-pipeline.md).

### Observability

```bash
python -m llm_observability_analytics.cli.main --summary      # uses configs/observability.yaml
```

Common flags:

- `--summary` — interaction/retrieval counts and latency stats.
- `--schema` — print the detected schema for loaded events.
- `--start-time` / `--end-time` — ISO-8601 timestamp filter.
- `--export-csv PATH` / `--export-parquet PATH` — write `<path>_interactions.*` and `<path>_retrievals.*`.
- `--detect-anomalies` — events with latency outliers (>3σ) or missing required fields.
- `--validate` — report invalid events; pair with `--filter-invalid` to continue past errors.

Subcommands:

```bash
python -m llm_observability_analytics.cli.main validate-config configs/observability.yaml
python -m llm_observability_analytics.cli.main diff-contracts old.json new.json
python -m llm_observability_analytics.cli.main visualize-pipeline configs/observability.yaml
python -m llm_observability_analytics.cli.main coverage-report
```

## Development

```bash
make format     # ruff format
make lint       # ruff check
make typecheck  # mypy src
make test       # pytest
make ci         # lint + typecheck + test
```

Because the three packages each have their own test modules with overlapping names, run grouped tests to avoid pytest collection collisions:

```bash
python -m scripts.run_tests_by_package
```

End-to-end smoke test across all three CLIs:

```bash
pytest tests/test_end_to_end_pipeline.py
```

### Pre-commit hooks

```bash
pip install pre-commit
pre-commit install
```

See [.pre-commit-config.yaml](.pre-commit-config.yaml) for the hooks.

## Repository layout

```text
src/
  llm_knowledge_ingestion/   parsers, chunking, IO, normalize, pipeline, CLI
  llm_dataset_foundry/       ingest, quality, splits, versioning, reports, CLI
  llm_observability_analytics/ events, traces, metrics, storage, reports, CLI
tests/                        shared test suite (run via run_tests_by_package)
docs/                         architecture, integration, contracts, MVP guides
examples/                     sample documents and integration handoffs
configs/                      per-pipeline default configs (ingestion, foundry, observability)
scripts/                      bootstrap, grouped test runner, contract validator
.github/workflows/ci.yml      lint, type-check, CLI smoke checks, grouped tests
```

## Contracts and cross-repo consistency

Shared identifiers and handoff field requirements are defined in [docs/data-contracts.md](docs/data-contracts.md) and summarized machine-readably in [docs/shared-contract-summary.json](docs/shared-contract-summary.json). Validate locally with:

```bash
python scripts/validate_shared_contracts.py
```

See [docs/contract-consistency.md](docs/contract-consistency.md) for the safe-update process.

## CI

[.github/workflows/ci.yml](.github/workflows/ci.yml) runs `ruff check`, `mypy`, `--help` smoke checks for all three CLIs, and the grouped test suite on every push and PR.

## License

See [LICENSE](LICENSE).
