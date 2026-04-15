from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-observability")
    parser.add_argument(
        "--config",
        default="configs/base.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and module wiring without processing events",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.dry_run:
        print(f"Dry run successful. Config: {args.config}")
        return 0

    import json
    from pathlib import Path

    from llm_observability_analytics.events.loader import (
        load_interaction_events,
        load_retrieval_trace_events,
    )
    from llm_observability_analytics.pipeline.config import load_config

    config = load_config(Path(args.config))
    try:
        interactions = load_interaction_events(
            config.events.interactions_path,
            config.events.max_events,
        )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Failed to load interaction events: {exc}")
        interactions = []
    try:
        retrievals = load_retrieval_trace_events(
            config.events.retrievals_path,
            config.events.max_events,
        )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Failed to load retrieval trace events: {exc}")
        retrievals = []

    summary = {
        "interactions_loaded": len(interactions),
        "retrievals_loaded": len(retrievals),
        "interactions_path": str(config.events.interactions_path),
        "retrievals_path": str(config.events.retrievals_path),
    }

    # Write summary to output.summary_path
    try:
        config.output.summary_path.parent.mkdir(parents=True, exist_ok=True)
        with config.output.summary_path.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Event processing complete. Summary written to {config.output.summary_path}")
    except (OSError, ValueError) as exc:
        print(f"Failed to write summary: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
