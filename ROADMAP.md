# Roadmap

Tracked in GitHub via milestones. Each milestone has a small set of epic issues with checklists of concrete sub-tasks.

## Active milestones

- [`coverage-parity-v1`](#coverage-parity-v1) — uniform 75% coverage gate across all three packages
- [`production-ingestion-v1`](#production-ingestion-v1) — move `llm_knowledge_ingestion` from MVP toward production-grade

## coverage-parity-v1

[Milestone on GitHub](https://github.com/DiogoRibeiro7/llm-data-platform/milestone/1)

**Why:** `llm_observability_analytics` ships with a 75% coverage gate enforced in CI. `llm_knowledge_ingestion` and `llm_dataset_foundry` do not. Today a regression in foundry coverage to 0% would pass CI. The goal of this milestone is to bring all three packages to the same gate and enforce it uniformly.

### Status (as of 2026-05-11)

Measured via `python -m scripts.run_tests_by_package`:

| Package | Coverage | Gate | Gap |
| --- | --- | --- | --- |
| `llm_observability_analytics` | 80% | 75% (enforced) | — |
| `llm_knowledge_ingestion` | 76% | none | parsers/base.py at 0% |
| `llm_dataset_foundry` | 50% | none | 8 modules at 0%, 4 partially covered |

### Coverage epics

1. **[#22 — Bring `llm_knowledge_ingestion` to 75% coverage gate](https://github.com/DiogoRibeiro7/llm-data-platform/issues/22)**
   - Smallest lift: only `parsers/base.py` needs new tests. Already at 76% in aggregate.

2. **[#23 — Bring `llm_dataset_foundry` to 75% coverage gate](https://github.com/DiogoRibeiro7/llm-data-platform/issues/23)**
   - Largest lift: pipeline config + orchestrator + CLI + reports writer all sit at 0% when measured by the grouped test runner. End-to-end test exercises some of this but coverage isn't attributed to the foundry package.

3. **[#24 — Enforce uniform 75% coverage gate across all packages](https://github.com/DiogoRibeiro7/llm-data-platform/issues/24)**
   - Once #22 and #23 land, change `scripts/run_tests_by_package.py` from a per-package hardcoded threshold to a uniform mapping, and remove the observability-specific `--cov` from `pyproject.toml`.

### Coverage rollout order

Issues #22 and #23 can land in parallel. #24 lands last and flips the gate on.

## production-ingestion-v1

[Milestone on GitHub](https://github.com/DiogoRibeiro7/llm-data-platform/milestone/2)

**Why:** `llm_knowledge_ingestion` is explicitly an MVP today. Parser classes for PDF/HTML/Markdown raise `NotImplementedError`. Chunking is whitespace-window only with a hardcoded guard against any other strategy. The dedup module computes hashes but nothing compares them. Sources are local filesystem only. A single bad file aborts the whole run. This milestone closes those gaps.

### Ingestion epics

1. **[#25 — Real document parsers (PDF, HTML, Markdown-aware, JSON paths)](https://github.com/DiogoRibeiro7/llm-data-platform/issues/25)**
   - Replace the `NotImplementedError` stubs and wire the live pipeline through the parsers module instead of the inline dispatch in `io/local_files.py`.

2. **[#26 — Smarter chunking (sentence + heading-aware, real tokenizer)](https://github.com/DiogoRibeiro7/llm-data-platform/issues/26)**
   - Add `sentence_aware` and `heading_aware` strategies alongside `fixed_tokens`; plug in a real tokenizer behind an optional extra with a whitespace fallback.

3. **[#27 — Pluggable sources (remote + streaming)](https://github.com/DiogoRibeiro7/llm-data-platform/issues/27)**
   - Define a `SourceReader` protocol, add S3 and HTTP readers behind optional extras, support streaming reads so large files don't OOM.

4. **[#28 — Idempotent runs with real deduplication](https://github.com/DiogoRibeiro7/llm-data-platform/issues/28)**
   - Detect content-hash duplicates, collapse them, write a `dedup_report.jsonl`, and persist run state so re-runs skip unchanged files.

5. **[#29 — Operational hardening (errors, observability hooks, exit codes)](https://github.com/DiogoRibeiro7/llm-data-platform/issues/29)**
   - Per-file error isolation, a documented exit-code contract, structured logging, and a per-run summary artifact that `llm_observability_analytics` can ingest.

### Ingestion rollout order

- **#25 and #26 are coupled.** Heading-aware chunking depends on parser-emitted structure, so #25 should land first or be developed in coordination with #26.
- **#27 is independent** and can ship in parallel.
- **#28 and #29 build on the others.** Idempotent runs need parsers/sources stable enough that "unchanged" is a well-defined state. Operational hardening uses the error surfaces added by earlier epics.

A reasonable phasing: #25 → #26 in parallel with #27 → #28 → #29.

### Deferred from this milestone

- OCR for image-only PDFs.
- DOCX/PPTX parsers.
- Pre-computed embedding outputs (downstream of `embedding-ready` enrichment).
- Authenticated source readers (secrets manager integration).

If any of these become urgent, file a `production-ingestion-v2` milestone with the relevant epics.

## Process

- Roadmap items live in GitHub milestones, not in this file. This file is a human-readable index that points at them.
- Each epic issue carries the concrete sub-task checklist. Sub-tasks become real issues only if they grow large enough to warrant their own discussion.
- When a milestone closes, summarize it here under a "Past milestones" section so the history stays visible.
