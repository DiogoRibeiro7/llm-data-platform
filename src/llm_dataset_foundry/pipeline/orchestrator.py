from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from llm_dataset_foundry.contracts.models import DatasetManifest, DatasetVersionMetadata
from llm_dataset_foundry.ingest.local_loader import (
    load_interaction_traces,
    load_normalized_documents,
    load_retrieval_traces,
)
from llm_dataset_foundry.ingest.transform import (
    build_prompt_response_dataset,
    build_retrieval_eval_dataset,
)
from llm_dataset_foundry.pipeline.config import PipelineConfig
from llm_dataset_foundry.quality.checks import quality_summary, run_quality_checks
from llm_dataset_foundry.reports.writers import (
    write_manifest,
    write_prompt_response,
    write_quality_report,
    write_retrieval_eval,
    write_split_assignments,
    write_version_metadata,
)
from llm_dataset_foundry.splits.models import SplitAssignment
from llm_dataset_foundry.splits.strategies import assign_split, split_counts


@dataclass(frozen=True, slots=True)
class PipelineRunResult:
    documents_loaded: int
    interaction_traces_loaded: int
    retrieval_traces_loaded: int
    prompt_response_records: int
    retrieval_eval_records: int


@dataclass(slots=True)
class DatasetFoundryPipeline:
    config: PipelineConfig

    def run(self) -> PipelineRunResult:
        docs = load_normalized_documents(
            self.config.ingest.normalized_documents_file, self.config.ingest.max_records
        )
        interaction_traces = load_interaction_traces(
            self.config.ingest.interaction_events_file, self.config.ingest.max_records
        )
        retrieval_traces = load_retrieval_traces(
            self.config.ingest.retrieval_events_file, self.config.ingest.max_records
        )

        prompt_response = build_prompt_response_dataset(
            interaction_traces,
            dataset_id=self.config.dataset.dataset_id,
            dataset_version=self.config.dataset.dataset_version,
        )
        retrieval_eval = build_retrieval_eval_dataset(
            retrieval_traces,
            dataset_id=self.config.dataset.dataset_id,
            dataset_version=self.config.dataset.dataset_version,
            model_version=self.config.dataset.model_version,
        )

        checks = run_quality_checks(
            dataset_id=self.config.dataset.dataset_id,
            dataset_version=self.config.dataset.dataset_version,
            prompt_response=prompt_response,
            retrieval_eval=retrieval_eval,
            min_text_length=self.config.quality.min_text_length,
            dedup_enabled=self.config.quality.dedup_enabled,
        )

        split_assignments: list[SplitAssignment] = []
        for record in prompt_response:
            split_assignments.append(
                SplitAssignment(
                    record_id=record.record_id,
                    split=assign_split(
                        record.record_id,
                        seed=self.config.splits.seed,
                        train_ratio=self.config.splits.train_ratio,
                        validation_ratio=self.config.splits.validation_ratio,
                    ),
                )
            )
        for retrieval_record in retrieval_eval:
            split_assignments.append(
                SplitAssignment(
                    record_id=retrieval_record.record_id,
                    split=assign_split(
                        retrieval_record.record_id,
                        seed=self.config.splits.seed,
                        train_ratio=self.config.splits.train_ratio,
                        validation_ratio=self.config.splits.validation_ratio,
                    ),
                )
            )

        counts_by_split = split_counts(
            prompt_response,
            retrieval_eval,
            seed=self.config.splits.seed,
            train_ratio=self.config.splits.train_ratio,
            validation_ratio=self.config.splits.validation_ratio,
        )
        counts = {
            "prompt_response": len(prompt_response),
            "retrieval_evaluation": len(retrieval_eval),
            **counts_by_split,
        }

        now = datetime.now(tz=UTC)
        manifest = DatasetManifest(
            dataset_name=self.config.dataset.dataset_name,
            dataset_id=self.config.dataset.dataset_id,
            dataset_version=self.config.dataset.dataset_version,
            generation_timestamp=now,
            record_counts=counts,
            source_references=[
                str(self.config.ingest.normalized_documents_file),
                str(self.config.ingest.interaction_events_file),
                str(self.config.ingest.retrieval_events_file),
            ],
            schema_version=self.config.dataset.schema_version,
            generation_parameters={
                "seed": str(self.config.splits.seed),
                "train_ratio": str(self.config.splits.train_ratio),
                "validation_ratio": str(self.config.splits.validation_ratio),
                "test_ratio": str(self.config.splits.test_ratio),
            },
            quality_summary=quality_summary(checks),
            model_version=self.config.dataset.model_version,
        )
        version_metadata = DatasetVersionMetadata(
            dataset_id=self.config.dataset.dataset_id,
            dataset_version=self.config.dataset.dataset_version,
            created_at=now,
            status="generated",
            model_version=self.config.dataset.model_version,
            notes="MVP local run",
        )

        base = self.config.output.curated_dataset_path
        write_prompt_response(base / "prompt_response.jsonl", prompt_response)
        write_retrieval_eval(base / "retrieval_evaluation.jsonl", retrieval_eval)
        write_split_assignments(base / "split_assignments.jsonl", split_assignments)
        write_quality_report(self.config.output.reports_path / "quality_report.json", checks)
        write_manifest(self.config.output.manifests_path / "dataset_manifest.json", manifest)
        write_version_metadata(
            self.config.output.manifests_path / "dataset_version_metadata.json",
            version_metadata,
        )

        return PipelineRunResult(
            documents_loaded=len(docs),
            interaction_traces_loaded=len(interaction_traces),
            retrieval_traces_loaded=len(retrieval_traces),
            prompt_response_records=len(prompt_response),
            retrieval_eval_records=len(retrieval_eval),
        )
