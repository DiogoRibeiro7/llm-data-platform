from __future__ import annotations

import argparse
from pathlib import Path

from llm_dataset_foundry.pipeline.config import load_config
from llm_dataset_foundry.pipeline.orchestrator import DatasetFoundryPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-dataset-foundry")
    parser.add_argument("--config", default="configs/base.yaml", help="Path to configuration file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and module wiring without building datasets",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(Path(args.config))

    if args.dry_run:
        print(
            "Dry run successful: "
            f"dataset={config.dataset.dataset_id}@{config.dataset.dataset_version} "
            f"docs={config.ingest.normalized_documents_file} "
            f"interactions={config.ingest.interaction_events_file} "
            f"retrieval={config.ingest.retrieval_events_file}"
        )
        return 0

    result = DatasetFoundryPipeline(config=config).run()
    print(
        "Dataset build completed: "
        f"documents={result.documents_loaded} "
        f"prompt_response={result.prompt_response_records} "
        f"retrieval_eval={result.retrieval_eval_records}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
