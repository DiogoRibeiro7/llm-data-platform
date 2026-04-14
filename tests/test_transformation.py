from __future__ import annotations

from llm_dataset_foundry.ingest.local_loader import (
    InteractionTraceInput,
    RetrievalRefInput,
    RetrievalTraceInput,
)
from llm_dataset_foundry.ingest.transform import (
    build_prompt_response_dataset,
    build_retrieval_eval_dataset,
)


def test_build_prompt_response_dataset() -> None:
    traces = [
        InteractionTraceInput(
            query_id="qry-1",
            trace_id="trc-1",
            prompt_text="Prompt",
            response_text="Response",
            model_version="m-1",
            retrieval_references=[RetrievalRefInput(document_id="doc-1", chunk_id="chk-1")],
        )
    ]
    records = build_prompt_response_dataset(traces, dataset_id="ds-1", dataset_version="v1")
    assert len(records) == 1
    assert records[0].query_id == "qry-1"
    assert records[0].document_id == "doc-1"


def test_build_retrieval_eval_dataset() -> None:
    traces = [
        RetrievalTraceInput(
            query_id="qry-1",
            trace_id="trc-1",
            expected_document_id="doc-1",
            expected_chunk_id="chk-1",
            retrieved=[RetrievalRefInput(document_id="doc-1", chunk_id="chk-1")],
        )
    ]
    records = build_retrieval_eval_dataset(
        traces, dataset_id="ds-1", dataset_version="v1", model_version="m-1"
    )
    assert len(records) == 1
    assert records[0].retrieved[0].rank == 0
