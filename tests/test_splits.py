from llm_dataset_foundry.splits.strategies import assign_split


def test_split_reproducibility() -> None:
    first = [
        assign_split(record_id=f"rec-{idx}", seed=42, train_ratio=0.8, validation_ratio=0.1)
        for idx in range(20)
    ]
    second = [
        assign_split(record_id=f"rec-{idx}", seed=42, train_ratio=0.8, validation_ratio=0.1)
        for idx in range(20)
    ]
    assert first == second
