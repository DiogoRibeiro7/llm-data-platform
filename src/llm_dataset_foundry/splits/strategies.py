from __future__ import annotations

import hashlib

from llm_dataset_foundry.contracts.models import (
    PromptResponseTrainingExample,
    RetrievalEvaluationExample,
)


def _bucket(value: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}|{value}".encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def assign_split(
    record_id: str,
    *,
    seed: int,
    train_ratio: float,
    validation_ratio: float,
) -> str:
    p = _bucket(record_id, seed)
    if p < train_ratio:
        return "train"
    if p < train_ratio + validation_ratio:
        return "validation"
    return "test"


def apply_splits_to_prompt_response(
    records: list[PromptResponseTrainingExample],
    *,
    seed: int,
    train_ratio: float,
    validation_ratio: float,
) -> list[PromptResponseTrainingExample]:
    updated: list[PromptResponseTrainingExample] = []
    for record in records:
        split = assign_split(
            record.record_id,
            seed=seed,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
        )
        updated.append(PromptResponseTrainingExample.from_dict({**record.to_dict(), "metadata": {"split": split}}))
    return updated


def split_counts(
    prompt_response_records: list[PromptResponseTrainingExample],
    retrieval_records: list[RetrievalEvaluationExample],
    *,
    seed: int,
    train_ratio: float,
    validation_ratio: float,
) -> dict[str, int]:
    counts = {"train": 0, "validation": 0, "test": 0}
    for record in prompt_response_records:
        split = assign_split(
            record.record_id,
            seed=seed,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
        )
        counts[split] += 1
    for retrieval_record in retrieval_records:
        split = assign_split(
            retrieval_record.record_id,
            seed=seed,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
        )
        counts[split] += 1
    return counts
