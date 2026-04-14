from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast


@dataclass(frozen=True, slots=True)
class NormalizedDocumentInput:
    document_id: str
    source_id: str
    title: str
    content: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RetrievalRefInput:
    document_id: str
    chunk_id: str


@dataclass(frozen=True, slots=True)
class InteractionTraceInput:
    query_id: str
    trace_id: str
    prompt_text: str
    response_text: str
    model_version: str
    retrieval_references: list[RetrievalRefInput] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class RetrievalTraceInput:
    query_id: str
    trace_id: str
    expected_document_id: str | None
    expected_chunk_id: str | None
    retrieved: list[RetrievalRefInput] = field(default_factory=list)


def _read_jsonl(path: Path, max_records: int) -> list[dict[str, Any]]:
    if not path.exists():
        raise ValueError(f"Input file does not exist: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path}:{line_no}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"Expected object JSON in {path}:{line_no}")
            rows.append(payload)
            if len(rows) >= max_records:
                break
    return rows


def load_normalized_documents(path: Path, max_records: int) -> list[NormalizedDocumentInput]:
    docs: list[NormalizedDocumentInput] = []
    for payload in _read_jsonl(path, max_records):
        docs.append(
            NormalizedDocumentInput(
                document_id=str(payload["document_id"]),
                source_id=str(payload.get("source_id", "")),
                title=str(payload.get("title", "")),
                content=str(payload.get("content", "")),
                metadata={str(k): str(v) for k, v in dict(payload.get("metadata", {})).items()},
            )
        )
    return docs


def load_interaction_traces(path: Path, max_records: int) -> list[InteractionTraceInput]:
    traces: list[InteractionTraceInput] = []
    for payload in _read_jsonl(path, max_records):
        raw_refs = payload.get("retrieval_references", [])
        refs = [
            RetrievalRefInput(document_id=str(ref["document_id"]), chunk_id=str(ref["chunk_id"]))
            for ref in raw_refs
            if isinstance(ref, dict) and "document_id" in ref and "chunk_id" in ref
        ]
        model_context = payload.get("model_context", {})
        model_version = str(model_context.get("model_version", payload.get("model_version", "unknown-model")))
        traces.append(
            InteractionTraceInput(
                query_id=str(payload["query_id"]),
                trace_id=str(payload["trace_id"]),
                prompt_text=str(payload["prompt_text"]),
                response_text=str(payload["response_text"]),
                model_version=model_version,
                retrieval_references=refs,
            )
        )
    return traces


def load_retrieval_traces(path: Path, max_records: int) -> list[RetrievalTraceInput]:
    traces: list[RetrievalTraceInput] = []
    for payload in _read_jsonl(path, max_records):
        refs = [
            RetrievalRefInput(document_id=str(ref["document_id"]), chunk_id=str(ref["chunk_id"]))
            for ref in payload.get("retrieved", [])
            if isinstance(ref, dict) and "document_id" in ref and "chunk_id" in ref
        ]
        traces.append(
            RetrievalTraceInput(
                query_id=str(payload["query_id"]),
                trace_id=str(payload["trace_id"]),
                expected_document_id=cast(str | None, payload.get("expected_document_id")),
                expected_chunk_id=cast(str | None, payload.get("expected_chunk_id")),
                retrieved=refs,
            )
        )
    return traces
