from llm_dataset_foundry.contracts.models import (
    PromptResponseTrainingExample,
    RetrievalEvaluationExample,
)
from llm_dataset_foundry.quality.checks import run_quality_checks


def test_quality_checks_detect_short_text() -> None:
    prompt_records = [
        PromptResponseTrainingExample(
            dataset_id="ds-1",
            dataset_version="v1",
            record_id="rec-1",
            prompt="short",
            response="ok",
        )
    ]
    retrieval_records: list[RetrievalEvaluationExample] = []
    checks = run_quality_checks(
        dataset_id="ds-1",
        dataset_version="v1",
        prompt_response=prompt_records,
        retrieval_eval=retrieval_records,
        min_text_length=10,
        dedup_enabled=True,
    )
    min_len = next(c for c in checks if c.check_name == "min_text_length")
    assert min_len.passed is False
    assert min_len.violations == 1
