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

