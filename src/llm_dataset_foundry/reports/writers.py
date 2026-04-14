from __future__ import annotations

import json
from pathlib import Path

from llm_dataset_foundry.contracts.models import (
    DatasetManifest,
    DatasetVersionMetadata,
    PromptResponseTrainingExample,
    QualityValidationResult,
    RetrievalEvaluationExample,
)
from llm_dataset_foundry.splits.models import SplitAssignment


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True))
            handle.write("\n")


def write_prompt_response(path: Path, rows: list[PromptResponseTrainingExample]) -> None:
    _write_jsonl(path, [row.to_dict() for row in rows])


def write_retrieval_eval(path: Path, rows: list[RetrievalEvaluationExample]) -> None:
    _write_jsonl(path, [row.to_dict() for row in rows])


def write_split_assignments(path: Path, rows: list[SplitAssignment]) -> None:
    _write_jsonl(path, [{"record_id": row.record_id, "split": row.split} for row in rows])


def write_quality_report(path: Path, checks: list[QualityValidationResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([check.to_dict() for check in checks], sort_keys=True, indent=2), encoding="utf-8")


def write_manifest(path: Path, manifest: DatasetManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.to_json(), encoding="utf-8")


def write_version_metadata(path: Path, metadata: DatasetVersionMetadata) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(metadata.to_json(), encoding="utf-8")
