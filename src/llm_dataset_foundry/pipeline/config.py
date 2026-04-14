from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True, slots=True)
class IngestSettings:
    normalized_documents_file: Path
    interaction_events_file: Path
    retrieval_events_file: Path
    max_records: int = 10000

    def __post_init__(self) -> None:
        if self.max_records <= 0:
            raise ValueError("ingest.max_records must be > 0")


@dataclass(frozen=True, slots=True)
class DatasetSettings:
    dataset_name: str
    dataset_id: str
    dataset_version: str
    schema_version: str
    model_version: str

    def __post_init__(self) -> None:
        if not self.dataset_name.strip():
            raise ValueError("dataset.dataset_name must not be empty")


@dataclass(frozen=True, slots=True)
class QualitySettings:
    dedup_enabled: bool
    min_text_length: int

    def __post_init__(self) -> None:
        if self.min_text_length <= 0:
            raise ValueError("quality.min_text_length must be > 0")


@dataclass(frozen=True, slots=True)
class SplitSettings:
    seed: int
    train_ratio: float
    validation_ratio: float
    test_ratio: float

    def __post_init__(self) -> None:
        total = self.train_ratio + self.validation_ratio + self.test_ratio
        if not (0.999 <= total <= 1.001):
            raise ValueError("split ratios must sum to 1.0")
        if self.train_ratio <= 0 or self.validation_ratio <= 0 or self.test_ratio <= 0:
            raise ValueError("all split ratios must be > 0")


@dataclass(frozen=True, slots=True)
class OutputSettings:
    curated_dataset_path: Path
    reports_path: Path
    manifests_path: Path


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    ingest: IngestSettings
    dataset: DatasetSettings
    quality: QualitySettings
    splits: SplitSettings
    output: OutputSettings


def _path(base_dir: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else (base_dir / candidate)


def _require_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Config key '{key}' must be a mapping")
    return value


def load_config(config_path: Path) -> PipelineConfig:
    base_dir = config_path.resolve().parent
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Config payload must be a mapping")

    ingest_data = _require_mapping(payload, "ingest")
    dataset_data = _require_mapping(payload, "dataset")
    quality_data = _require_mapping(payload, "quality")
    split_data = _require_mapping(payload, "splits")
    output_data = _require_mapping(payload, "output")

    ingest = IngestSettings(
        normalized_documents_file=_path(base_dir, str(ingest_data["normalized_documents_file"])),
        interaction_events_file=_path(base_dir, str(ingest_data["interaction_events_file"])),
        retrieval_events_file=_path(base_dir, str(ingest_data["retrieval_events_file"])),
        max_records=int(ingest_data.get("max_records", 10000)),
    )
    dataset = DatasetSettings(
        dataset_name=str(dataset_data["dataset_name"]),
        dataset_id=str(dataset_data["dataset_id"]),
        dataset_version=str(dataset_data["dataset_version"]),
        schema_version=str(dataset_data.get("schema_version", "1.0")),
        model_version=str(dataset_data.get("model_version", "unknown-model")),
    )
    quality = QualitySettings(
        dedup_enabled=bool(quality_data.get("dedup_enabled", True)),
        min_text_length=int(quality_data.get("min_text_length", 10)),
    )
    splits = SplitSettings(
        seed=int(split_data.get("seed", 42)),
        train_ratio=float(split_data.get("train_ratio", 0.8)),
        validation_ratio=float(split_data.get("validation_ratio", 0.1)),
        test_ratio=float(split_data.get("test_ratio", 0.1)),
    )
    output = OutputSettings(
        curated_dataset_path=_path(base_dir, str(output_data["curated_dataset_path"])),
        reports_path=_path(base_dir, str(output_data["reports_path"])),
        manifests_path=_path(base_dir, str(output_data["manifests_path"])),
    )
    return PipelineConfig(ingest=ingest, dataset=dataset, quality=quality, splits=splits, output=output)
