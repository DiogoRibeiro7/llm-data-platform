from __future__ import annotations

import hashlib

from llm_dataset_foundry.contracts.models import (
    PromptResponseTrainingExample,
    RetrievalEvaluationExample,
    RetrievedReference,
)
from llm_dataset_foundry.ingest.local_loader import InteractionTraceInput, RetrievalTraceInput


def _stable_id(seed: str) -> str:
    return f"rec_{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:24]}"


def build_prompt_response_dataset(
    traces: list[InteractionTraceInput],
    *,
    dataset_id: str,
    dataset_version: str,
) -> list[PromptResponseTrainingExample]:
    examples: list[PromptResponseTrainingExample] = []
    for trace in traces:
        first_ref = trace.retrieval_references[0] if trace.retrieval_references else None
        record_id = _stable_id(f"pr|{trace.query_id}|{trace.trace_id}")
        examples.append(
            PromptResponseTrainingExample(
                dataset_id=dataset_id,
                dataset_version=dataset_version,
                record_id=record_id,
                prompt=trace.prompt_text,
                response=trace.response_text,
                query_id=trace.query_id,
                trace_id=trace.trace_id,
                document_id=None if first_ref is None else first_ref.document_id,
                chunk_id=None if first_ref is None else first_ref.chunk_id,
                model_version=trace.model_version,
            )
        )
    return examples


def build_retrieval_eval_dataset(
    traces: list[RetrievalTraceInput],
    *,
    dataset_id: str,
    dataset_version: str,
    model_version: str,
) -> list[RetrievalEvaluationExample]:
    examples: list[RetrievalEvaluationExample] = []
    for trace in traces:
        retrieved = [
            RetrievedReference(document_id=ref.document_id, chunk_id=ref.chunk_id, rank=rank)
            for rank, ref in enumerate(trace.retrieved)
        ]
        record_id = _stable_id(f"ret|{trace.query_id}|{trace.trace_id}")
        examples.append(
            RetrievalEvaluationExample(
                dataset_id=dataset_id,
                dataset_version=dataset_version,
                record_id=record_id,
                query_id=trace.query_id,
                trace_id=trace.trace_id,
                expected_document_id=trace.expected_document_id,
                expected_chunk_id=trace.expected_chunk_id,
                retrieved=retrieved,
                model_version=model_version,
            )
        )
    return examples
