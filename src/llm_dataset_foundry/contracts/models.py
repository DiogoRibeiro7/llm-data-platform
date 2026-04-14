from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, cast

DATASET_CONTRACT_VERSION = "1.0"
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{1,127}$")


def _assert_non_empty(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def _assert_id(value: str, name: str) -> None:
    _assert_non_empty(value, name)
    if not ID_PATTERN.fullmatch(value):
        raise ValueError(f"{name} must match {ID_PATTERN.pattern}")


def _assert_tz_aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError(f"{name} must be timezone-aware")


def _assert_contract_version(value: str) -> None:
    if value != DATASET_CONTRACT_VERSION:
        raise ValueError(
            f"Unsupported contract_version={value!r}; expected {DATASET_CONTRACT_VERSION!r}"
        )


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_serialize(inner) for inner in value]
    return value


class ContractModel:
    def to_dict(self) -> dict[str, Any]:
        return cast(dict[str, Any], _serialize(asdict(cast(Any, self))))

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


@dataclass(frozen=True, slots=True)
class DatasetRecord(ContractModel):
    dataset_id: str
    dataset_version: str
    record_id: str
    document_id: str | None = None
    chunk_id: str | None = None
    query_id: str | None = None
    trace_id: str | None = None
    model_version: str | None = None
    split: str | None = None
    input_text: str | None = None
    target_text: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    contract_version: str = DATASET_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_id(self.dataset_id, "dataset_id")
        _assert_non_empty(self.dataset_version, "dataset_version")
        _assert_id(self.record_id, "record_id")
        if self.document_id is not None:
            _assert_id(self.document_id, "document_id")
        if self.chunk_id is not None:
            _assert_id(self.chunk_id, "chunk_id")
        if self.query_id is not None:
            _assert_id(self.query_id, "query_id")
        if self.trace_id is not None:
            _assert_id(self.trace_id, "trace_id")
        if self.model_version is not None:
            _assert_non_empty(self.model_version, "model_version")
        if self.split is not None:
            _assert_non_empty(self.split, "split")
        if self.chunk_id is not None and self.document_id is None:
            raise ValueError("document_id is required when chunk_id is set")
        if self.trace_id is not None and self.query_id is None:
            raise ValueError("query_id is required when trace_id is set")
        _assert_contract_version(self.contract_version)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> DatasetRecord:
        return cls(
            dataset_id=str(payload["dataset_id"]),
            dataset_version=str(payload["dataset_version"]),
            record_id=str(payload["record_id"]),
            document_id=cast(str | None, payload.get("document_id")),
            chunk_id=cast(str | None, payload.get("chunk_id")),
            query_id=cast(str | None, payload.get("query_id")),
            trace_id=cast(str | None, payload.get("trace_id")),
            model_version=cast(str | None, payload.get("model_version")),
            split=cast(str | None, payload.get("split")),
            input_text=cast(str | None, payload.get("input_text")),
            target_text=cast(str | None, payload.get("target_text")),
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata", {})).items()},
            contract_version=str(payload.get("contract_version", DATASET_CONTRACT_VERSION)),
        )

    @classmethod
    def from_json(cls, payload: str) -> DatasetRecord:
        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True, slots=True)
class PromptResponseTrainingExample(ContractModel):
    dataset_id: str
    dataset_version: str
    record_id: str
    prompt: str
    response: str
    query_id: str | None = None
    trace_id: str | None = None
    document_id: str | None = None
    chunk_id: str | None = None
    model_version: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    contract_version: str = DATASET_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_id(self.dataset_id, "dataset_id")
        _assert_non_empty(self.dataset_version, "dataset_version")
        _assert_id(self.record_id, "record_id")
        _assert_non_empty(self.prompt, "prompt")
        _assert_non_empty(self.response, "response")
        if self.query_id is not None:
            _assert_id(self.query_id, "query_id")
        if self.trace_id is not None:
            _assert_id(self.trace_id, "trace_id")
        if self.document_id is not None:
            _assert_id(self.document_id, "document_id")
        if self.chunk_id is not None:
            _assert_id(self.chunk_id, "chunk_id")
        if self.model_version is not None:
            _assert_non_empty(self.model_version, "model_version")
        if self.trace_id is not None and self.query_id is None:
            raise ValueError("query_id is required when trace_id is set")
        if self.chunk_id is not None and self.document_id is None:
            raise ValueError("document_id is required when chunk_id is set")
        _assert_contract_version(self.contract_version)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> PromptResponseTrainingExample:
        return cls(
            dataset_id=str(payload["dataset_id"]),
            dataset_version=str(payload["dataset_version"]),
            record_id=str(payload["record_id"]),
            prompt=str(payload["prompt"]),
            response=str(payload["response"]),
            query_id=cast(str | None, payload.get("query_id")),
            trace_id=cast(str | None, payload.get("trace_id")),
            document_id=cast(str | None, payload.get("document_id")),
            chunk_id=cast(str | None, payload.get("chunk_id")),
            model_version=cast(str | None, payload.get("model_version")),
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata", {})).items()},
            contract_version=str(payload.get("contract_version", DATASET_CONTRACT_VERSION)),
        )

    @classmethod
    def from_json(cls, payload: str) -> PromptResponseTrainingExample:
        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True, slots=True)
class RetrievedReference(ContractModel):
    document_id: str
    chunk_id: str
    rank: int
    score: float | None = None

    def __post_init__(self) -> None:
        _assert_id(self.document_id, "document_id")
        _assert_id(self.chunk_id, "chunk_id")
        if self.rank < 0:
            raise ValueError("rank must be >= 0")
        if self.score is not None and self.score < 0:
            raise ValueError("score must be >= 0")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RetrievedReference:
        return cls(
            document_id=str(payload["document_id"]),
            chunk_id=str(payload["chunk_id"]),
            rank=int(payload["rank"]),
            score=cast(float | None, payload.get("score")),
        )


@dataclass(frozen=True, slots=True)
class RetrievalEvaluationExample(ContractModel):
    dataset_id: str
    dataset_version: str
    record_id: str
    query_id: str
    trace_id: str
    expected_document_id: str | None = None
    expected_chunk_id: str | None = None
    retrieved: list[RetrievedReference] = field(default_factory=list)
    model_version: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    contract_version: str = DATASET_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_id(self.dataset_id, "dataset_id")
        _assert_non_empty(self.dataset_version, "dataset_version")
        _assert_id(self.record_id, "record_id")
        _assert_id(self.query_id, "query_id")
        _assert_id(self.trace_id, "trace_id")
        if self.expected_document_id is not None:
            _assert_id(self.expected_document_id, "expected_document_id")
        if self.expected_chunk_id is not None:
            _assert_id(self.expected_chunk_id, "expected_chunk_id")
        if self.expected_chunk_id is not None and self.expected_document_id is None:
            raise ValueError("expected_document_id is required when expected_chunk_id is set")
        if self.model_version is not None:
            _assert_non_empty(self.model_version, "model_version")
        _assert_contract_version(self.contract_version)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RetrievalEvaluationExample:
        retrieved = [
            item if isinstance(item, RetrievedReference) else RetrievedReference.from_dict(item)
            for item in payload.get("retrieved", [])
        ]
        return cls(
            dataset_id=str(payload["dataset_id"]),
            dataset_version=str(payload["dataset_version"]),
            record_id=str(payload["record_id"]),
            query_id=str(payload["query_id"]),
            trace_id=str(payload["trace_id"]),
            expected_document_id=cast(str | None, payload.get("expected_document_id")),
            expected_chunk_id=cast(str | None, payload.get("expected_chunk_id")),
            retrieved=retrieved,
            model_version=cast(str | None, payload.get("model_version")),
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata", {})).items()},
            contract_version=str(payload.get("contract_version", DATASET_CONTRACT_VERSION)),
        )

    @classmethod
    def from_json(cls, payload: str) -> RetrievalEvaluationExample:
        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True, slots=True)
class QualityValidationResult(ContractModel):
    dataset_id: str
    dataset_version: str
    check_name: str
    passed: bool
    severity: str
    checked_at: datetime
    violations: int = 0
    sample_record_ids: list[str] = field(default_factory=list)
    summary: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
    contract_version: str = DATASET_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_id(self.dataset_id, "dataset_id")
        _assert_non_empty(self.dataset_version, "dataset_version")
        _assert_non_empty(self.check_name, "check_name")
        _assert_non_empty(self.severity, "severity")
        _assert_tz_aware(self.checked_at, "checked_at")
        if self.violations < 0:
            raise ValueError("violations must be >= 0")
        for record_id in self.sample_record_ids:
            _assert_id(record_id, "sample_record_ids[]")
        _assert_contract_version(self.contract_version)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> QualityValidationResult:
        return cls(
            dataset_id=str(payload["dataset_id"]),
            dataset_version=str(payload["dataset_version"]),
            check_name=str(payload["check_name"]),
            passed=bool(payload["passed"]),
            severity=str(payload["severity"]),
            checked_at=datetime.fromisoformat(str(payload["checked_at"])),
            violations=int(payload.get("violations", 0)),
            sample_record_ids=[str(v) for v in payload.get("sample_record_ids", [])],
            summary=str(payload.get("summary", "")),
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata", {})).items()},
            contract_version=str(payload.get("contract_version", DATASET_CONTRACT_VERSION)),
        )

    @classmethod
    def from_json(cls, payload: str) -> QualityValidationResult:
        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True, slots=True)
class DatasetVersionMetadata(ContractModel):
    dataset_id: str
    dataset_version: str
    created_at: datetime
    status: str
    model_version: str | None = None
    previous_version: str | None = None
    commit_hash: str | None = None
    notes: str | None = None
    contract_version: str = DATASET_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_id(self.dataset_id, "dataset_id")
        _assert_non_empty(self.dataset_version, "dataset_version")
        _assert_tz_aware(self.created_at, "created_at")
        _assert_non_empty(self.status, "status")
        if self.model_version is not None:
            _assert_non_empty(self.model_version, "model_version")
        if self.previous_version is not None:
            _assert_non_empty(self.previous_version, "previous_version")
        if self.commit_hash is not None:
            _assert_non_empty(self.commit_hash, "commit_hash")
        _assert_contract_version(self.contract_version)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> DatasetVersionMetadata:
        return cls(
            dataset_id=str(payload["dataset_id"]),
            dataset_version=str(payload["dataset_version"]),
            created_at=datetime.fromisoformat(str(payload["created_at"])),
            status=str(payload["status"]),
            model_version=cast(str | None, payload.get("model_version")),
            previous_version=cast(str | None, payload.get("previous_version")),
            commit_hash=cast(str | None, payload.get("commit_hash")),
            notes=cast(str | None, payload.get("notes")),
            contract_version=str(payload.get("contract_version", DATASET_CONTRACT_VERSION)),
        )

    @classmethod
    def from_json(cls, payload: str) -> DatasetVersionMetadata:
        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True, slots=True)
class DatasetManifest(ContractModel):
    dataset_name: str
    dataset_id: str
    dataset_version: str
    generation_timestamp: datetime
    record_counts: dict[str, int]
    source_references: list[str]
    schema_version: str
    generation_parameters: dict[str, str]
    quality_summary: dict[str, str]
    model_version: str | None = None
    contract_version: str = DATASET_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _assert_non_empty(self.dataset_name, "dataset_name")
        _assert_id(self.dataset_id, "dataset_id")
        _assert_non_empty(self.dataset_version, "dataset_version")
        _assert_tz_aware(self.generation_timestamp, "generation_timestamp")
        _assert_non_empty(self.schema_version, "schema_version")
        if not self.record_counts:
            raise ValueError("record_counts must not be empty")
        for split_name, count in self.record_counts.items():
            _assert_non_empty(split_name, "record_counts key")
            if count < 0:
                raise ValueError("record_counts values must be >= 0")
        for reference in self.source_references:
            _assert_non_empty(reference, "source_references[]")
        if self.model_version is not None:
            _assert_non_empty(self.model_version, "model_version")
        _assert_contract_version(self.contract_version)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> DatasetManifest:
        return cls(
            dataset_name=str(payload["dataset_name"]),
            dataset_id=str(payload["dataset_id"]),
            dataset_version=str(payload["dataset_version"]),
            generation_timestamp=datetime.fromisoformat(str(payload["generation_timestamp"])),
            record_counts={str(k): int(v) for k, v in dict(payload["record_counts"]).items()},
            source_references=[str(v) for v in payload.get("source_references", [])],
            schema_version=str(payload["schema_version"]),
            generation_parameters={
                str(k): str(v) for k, v in dict(payload.get("generation_parameters", {})).items()
            },
            quality_summary={str(k): str(v) for k, v in dict(payload.get("quality_summary", {})).items()},
            model_version=cast(str | None, payload.get("model_version")),
            contract_version=str(payload.get("contract_version", DATASET_CONTRACT_VERSION)),
        )

    @classmethod
    def from_json(cls, payload: str) -> DatasetManifest:
        return cls.from_dict(json.loads(payload))
