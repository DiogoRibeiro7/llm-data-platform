from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime

from llm_dataset_foundry.contracts.models import (
    PromptResponseTrainingExample,
    QualityValidationResult,
    RetrievalEvaluationExample,
)


def run_quality_checks(
    *,
    dataset_id: str,
    dataset_version: str,
    prompt_response: list[PromptResponseTrainingExample],
    retrieval_eval: list[RetrievalEvaluationExample],
    min_text_length: int,
    dedup_enabled: bool,
) -> list[QualityValidationResult]:
    now = datetime.now(tz=UTC)
    checks: list[QualityValidationResult] = []

    short_ids = [
        rec.record_id
        for rec in prompt_response
        if len(rec.prompt.strip()) < min_text_length or len(rec.response.strip()) < min_text_length
    ]
    checks.append(
        QualityValidationResult(
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            check_name="min_text_length",
            passed=len(short_ids) == 0,
            severity="error",
            checked_at=now,
            violations=len(short_ids),
            sample_record_ids=short_ids[:10],
            summary=f"{len(short_ids)} prompt-response records below minimum text length",
        )
    )

    duplicate_ids: list[str] = []
    if dedup_enabled:
        counts = Counter([rec.record_id for rec in prompt_response] + [rec.record_id for rec in retrieval_eval])
        duplicate_ids = [record_id for record_id, count in counts.items() if count > 1]
    checks.append(
        QualityValidationResult(
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            check_name="duplicate_record_id",
            passed=len(duplicate_ids) == 0,
            severity="error",
            checked_at=now,
            violations=len(duplicate_ids),
            sample_record_ids=duplicate_ids[:10],
            summary=f"{len(duplicate_ids)} duplicate record IDs found",
        )
    )

    missing_retrieved = [rec.record_id for rec in retrieval_eval if len(rec.retrieved) == 0]
    checks.append(
        QualityValidationResult(
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            check_name="retrieval_non_empty",
            passed=len(missing_retrieved) == 0,
            severity="warning",
            checked_at=now,
            violations=len(missing_retrieved),
            sample_record_ids=missing_retrieved[:10],
            summary=f"{len(missing_retrieved)} retrieval examples with empty candidates",
        )
    )

    return checks


def quality_summary(checks: list[QualityValidationResult]) -> dict[str, str]:
    total = len(checks)
    failed = len([check for check in checks if not check.passed])
    return {
        "total_checks": str(total),
        "failed_checks": str(failed),
        "status": "pass" if failed == 0 else "fail",
    }
