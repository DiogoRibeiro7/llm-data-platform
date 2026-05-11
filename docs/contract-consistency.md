# Contract Consistency Strategy

The three packages now live in one monorepo, so most contract drift is caught at PR time by shared tests. The mechanism documented here still applies for two cases:

1. Aligning with sibling repos that vendored an earlier version of one of these packages.
2. Catching unintentional schema drift inside the monorepo before it ships.

## Objective

Keep shared identifiers, field names, contract versions, and handoff formats aligned across:

- `llm_knowledge_ingestion`
- `llm_observability_analytics`
- `llm_dataset_foundry`

…and across any external repos that still consume these packages' artifacts.

## Mechanism

In-repo:

- [`docs/shared-contract-summary.json`](shared-contract-summary.json) — machine-readable summary of identifiers, contract versions, and handoff field requirements.
- [`scripts/validate_shared_contracts.py`](../scripts/validate_shared_contracts.py) — validates that the summary is internally consistent and that example artifacts contain required fields.

The summary defines:

- canonical shared identifiers and their semantics
- contract version constants per package
- required producer/consumer fields per handoff
- example artifact paths used during validation

## Local validation

```bash
python scripts/validate_shared_contracts.py
```

## Cross-repo alignment

When sibling repos exist on disk, pass their summaries with `--peer`:

```bash
python scripts/validate_shared_contracts.py \
  --peer ../llm-observability-analytics/docs/shared-contract-summary.json \
  --peer ../llm-dataset-foundry/docs/shared-contract-summary.json
```

## Safe update process

1. Propose the contract change in `docs/shared-contract-summary.json`.
2. Update the affected schema dataclasses, docs, and example artifacts in the same PR.
3. Run `python scripts/validate_shared_contracts.py` locally.
4. Open coordinated PRs in any sibling repos.
5. Update peer summaries and integration examples.
6. Run cross-repo validation with `--peer` before merging.
7. For breaking changes, bump the contract version constant and add migration notes to the PR description.

The `llm-observability` CLI also ships a `diff-contracts` subcommand that surfaces breaking field changes between two contract files:

```bash
python -m llm_observability_analytics.cli.main diff-contracts old.json new.json
```
