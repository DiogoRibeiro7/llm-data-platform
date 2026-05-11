# Roadmap

Tracked in GitHub via milestones. Each milestone has a small set of epic issues with checklists of concrete sub-tasks.

## Current milestone — `coverage-parity-v1`

[Milestone on GitHub](https://github.com/DiogoRibeiro7/llm-data-platform/milestone/1)

**Why:** `llm_observability_analytics` ships with a 75% coverage gate enforced in CI. `llm_knowledge_ingestion` and `llm_dataset_foundry` do not. Today a regression in foundry coverage to 0% would pass CI. The goal of this milestone is to bring all three packages to the same gate and enforce it uniformly.

### Status (as of 2026-05-11)

Measured via `python -m scripts.run_tests_by_package`:

| Package | Coverage | Gate | Gap |
| --- | --- | --- | --- |
| `llm_observability_analytics` | 80% | 75% (enforced) | — |
| `llm_knowledge_ingestion` | 76% | none | parsers/base.py at 0% |
| `llm_dataset_foundry` | 50% | none | 8 modules at 0%, 4 partially covered |

### Epics

1. **[#22 — Bring `llm_knowledge_ingestion` to 75% coverage gate](https://github.com/DiogoRibeiro7/llm-data-platform/issues/22)**
   - Smallest lift: only `parsers/base.py` needs new tests. Already at 76% in aggregate.

2. **[#23 — Bring `llm_dataset_foundry` to 75% coverage gate](https://github.com/DiogoRibeiro7/llm-data-platform/issues/23)**
   - Largest lift: pipeline config + orchestrator + CLI + reports writer all sit at 0% when measured by the grouped test runner. End-to-end test exercises some of this but coverage isn't attributed to the foundry package.

3. **[#24 — Enforce uniform 75% coverage gate across all packages](https://github.com/DiogoRibeiro7/llm-data-platform/issues/24)**
   - Once #22 and #23 land, change `scripts/run_tests_by_package.py` from a per-package hardcoded threshold to a uniform mapping, and remove the observability-specific `--cov` from `pyproject.toml`.

### Order of operations

#22 and #23 can land in parallel. #24 lands last and flips the gate on.

## Process

- Roadmap items live in GitHub milestones, not in this file. This file is a human-readable index that points at them.
- Each epic issue carries the concrete sub-task checklist. Sub-tasks become real issues only if they grow large enough to warrant their own discussion.
- When a milestone closes, summarize it here under a "Past milestones" section so the history stays visible.
