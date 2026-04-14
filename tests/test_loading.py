from __future__ import annotations

from pathlib import Path

import pytest

from llm_dataset_foundry.ingest.local_loader import (
    load_interaction_traces,
    load_normalized_documents,
    load_retrieval_traces,
)


def test_load_normalized_documents(tmp_path: Path) -> None:
    path = tmp_path / "docs.jsonl"
    path.write_text(
        '{"document_id":"doc-1","source_id":"src-1","title":"T","content":"Body"}\n',
        encoding="utf-8",
    )
    docs = load_normalized_documents(path, 10)
    assert len(docs) == 1
    assert docs[0].document_id == "doc-1"


def test_load_interaction_and_retrieval_traces(tmp_path: Path) -> None:
    interactions = tmp_path / "interactions.jsonl"
    interactions.write_text(
        '{"query_id":"q-1","trace_id":"t-1","prompt_text":"p","response_text":"r","model_context":{"model_version":"m-1"},"retrieval_references":[{"document_id":"doc-1","chunk_id":"chk-1"}]}\n',
        encoding="utf-8",
    )
    retrieval = tmp_path / "retrieval.jsonl"
    retrieval.write_text(
        '{"query_id":"q-1","trace_id":"t-1","expected_document_id":"doc-1","expected_chunk_id":"chk-1","retrieved":[{"document_id":"doc-1","chunk_id":"chk-1"}]}\n',
        encoding="utf-8",
    )

    interactions_loaded = load_interaction_traces(interactions, 10)
    retrieval_loaded = load_retrieval_traces(retrieval, 10)
    assert interactions_loaded[0].model_version == "m-1"
    assert retrieval_loaded[0].expected_document_id == "doc-1"


def test_load_invalid_json_raises(tmp_path: Path) -> None:
    path = tmp_path / "broken.jsonl"
    path.write_text("{bad-json}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_normalized_documents(path, 10)
