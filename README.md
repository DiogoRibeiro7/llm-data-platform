# llm-data-platform

Monorepo containing lightweight tools for ingesting, processing and observing LLM data workflows.

Included packages

- `llm_knowledge_ingestion` — parsers, chunking, sources and pipeline interfaces.
- `llm_dataset_foundry` — dataset curation utilities and ingestion consumers.
- `llm_observability_analytics` — runtime telemetry, traces and analytics.

This repository consolidates the three components above to simplify development and CI.

Quickstart

Prerequisites:

- Python 3.12+
- Optional: `make` for convenience targets

Setup (Unix/macOS):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e '.[dev]'
```

Setup (Windows PowerShell):

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
```

Install profiles

- Base install: `pip install -e .`
- Development install: `pip install -e ".[dev]"`
- Observability CLI feature deps: `pip install -e ".[observability-cli]"`
- Observability CLI + parquet export: `pip install -e ".[observability-cli,parquet]"`

Development commands

- Format: `make format` (runs `ruff format`) 
- Lint: `make lint` (runs `ruff check`)
- Type check: `make typecheck` (runs `mypy src`)
- Tests: `make test` (runs `pytest`) or `python -m scripts.run_tests_by_package` to run tests grouped by package


Testing notes

This monorepo contains tests for multiple packages. Use the provided script to run tests grouped by package to avoid pytest collection collisions:

```bash
python -m scripts.run_tests_by_package
```

End-to-end pipeline test

To verify the full workflow (ingestion → dataset curation → observability analytics), run the end-to-end integration test:

```bash
pytest tests/test_end_to_end_pipeline.py
```
This test runs all main CLIs in sequence with sample data and checks that all expected output artifacts are produced.

Continuous Integration

The GitHub Actions workflow is at [.github/workflows/ci.yml](.github/workflows/ci.yml). It runs lint, type-check and the grouped tests.

Contributing

- Open issues or PRs against `main`.
- Run `make format` and `make lint` before pushing.
- Add unit tests for new behavior and keep `mypy` passing.

Repository layout

- `src/` — source packages under `llm_dataset_foundry`, `llm_knowledge_ingestion`, `llm_observability_analytics`
- `tests/` — integration/unit tests
- `scripts/` — utility scripts (e.g., `run_tests_by_package.py`)
- `.github/workflows/ci.yml` — CI configuration

License

This project uses the repository `LICENSE` file.

Contact

For questions, open an issue or contact the maintainers via GitHub.

## llm_observability_analytics CLI Features

The `llm_observability_analytics` package provides a powerful CLI for event validation, analytics, and pipeline management.

### Main CLI Usage

```bash
python -m llm_observability_analytics.cli.main --config <config.yaml> [OPTIONS]
```

### Feature Dependencies

- `--validate` and `validate-config` require `jsonschema` via `.[observability-cli]`.
- `--detect-anomalies` requires `numpy` via `.[observability-cli]`.
- `--export-csv` and `--export-parquet` require `pandas` via `.[observability-cli]`.
- `--export-parquet` additionally requires `pyarrow` via `.[parquet]`.

#### Core Options

- `--summary`  
  Print a summary report of event types and basic statistics.

- `--schema`  
  Print the detected schema (fields, types, missing fields) for loaded events.

- `--start-time <ISO8601>` / `--end-time <ISO8601>`  
  Filter events by timestamp range (applies to `request_timestamp`/`retrieval_timestamp`).

- `--export-csv <path>`  
  Export filtered events to CSV files (creates `<path>_interactions.csv` and `<path>_retrievals.csv`).

- `--export-parquet <path>`  
  Export filtered events to Parquet files (creates `<path>_interactions.parquet` and `<path>_retrievals.parquet`).

- `--detect-anomalies`  
  Print events with anomalous latency (3+ stddev above mean) or missing required fields.

- `--validate`  
  Validate all events and print/report any invalid records.

- `--filter-invalid`  
  Skip invalid events when summarizing (otherwise, loading stops at first error).

#### Example

```bash
python -m llm_observability_analytics.cli.main --config configs/base.yaml --summary --schema --export-csv out/events.csv
```

---

### Advanced CLI Commands

#### Validate Config

Validate a YAML config file against the expected schema:

```bash
python -m llm_observability_analytics.cli.main validate-config <config.yaml>
```

#### Diff Contracts

Compare two contract/schema files and report breaking changes:

```bash
python -m llm_observability_analytics.cli.main diff-contracts <old_contract.json|yaml> <new_contract.json|yaml>
```

#### Visualize Pipeline

Generate a Mermaid diagram of the pipeline from a config file:

```bash
python -m llm_observability_analytics.cli.main visualize-pipeline <config.yaml>
```

#### Coverage Report

Run all tests and print a coverage summary:

```bash
python -m llm_observability_analytics.cli.main coverage-report
```

---

### Pre-commit Hooks

This repo includes a `.pre-commit-config.yaml` for linting, formatting, type-checking, and running tests before each commit.

**Setup:**

```bash
pip install pre-commit
pre-commit install
```

---

**See the CLI help (`--help`) for more options and details.**

