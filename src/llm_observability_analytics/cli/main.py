from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from llm_observability_analytics.events.loader import (
    load_interaction_events,
    load_interaction_events_with_validation,
    load_retrieval_trace_events,
    load_retrieval_trace_events_with_validation,
)
from llm_observability_analytics.pipeline.config import load_config


def _to_dict(event: Any) -> dict[str, Any]:
    if hasattr(event, "to_dict"):
        maybe_dict = event.to_dict()
        if isinstance(maybe_dict, dict):
            return maybe_dict
    if isinstance(event, dict):
        return event
    return {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-observability")
    parser.add_argument("--summary", action="store_true", help="Print summary report")
    parser.add_argument("--config", default="configs/base.yaml", help="Path to configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Validate config wiring only")
    parser.add_argument("--validate", action="store_true", help="Validate all events")
    parser.add_argument(
        "--filter-invalid",
        action="store_true",
        help="Skip invalid events instead of aborting",
    )
    parser.add_argument("--schema", action="store_true", help="Print detected schema")
    parser.add_argument("--start-time", type=str, default=None, help="ISO8601 start time")
    parser.add_argument("--end-time", type=str, default=None, help="ISO8601 end time")
    parser.add_argument("--export-csv", type=str, default=None, help="Export events to CSV")
    parser.add_argument("--export-parquet", type=str, default=None, help="Export events to Parquet")
    parser.add_argument("--detect-anomalies", action="store_true", help="Detect anomalies")
    return parser


def detect_schema(events: list[Any]) -> dict[str, list[str]]:
    schema: dict[str, set[str]] = defaultdict(set)
    for event in events:
        data = _to_dict(event)
        for key, value in data.items():
            typ = type(value)
            name = typ.__name__ if typ.__module__ == "builtins" else f"{typ.__module__}.{typ.__name__}"
            schema[key].add(name)
    return {key: sorted(value) for key, value in schema.items()}


def filter_events_by_time(
    events: list[Any],
    start_time: str | None,
    end_time: str | None,
    timestamp_fields: list[str],
) -> list[Any]:
    if not start_time and not end_time:
        return events

    from datetime import datetime

    start = datetime.fromisoformat(start_time) if start_time else None
    end = datetime.fromisoformat(end_time) if end_time else None

    filtered: list[Any] = []
    for event in events:
        data = _to_dict(event)
        include = True
        for field in timestamp_fields:
            ts = data.get(field)
            if ts is None:
                continue
            value = datetime.fromisoformat(ts) if isinstance(ts, str) else ts
            if start is not None and value < start:
                include = False
                break
            if end is not None and value > end:
                include = False
                break
        if include:
            filtered.append(event)
    return filtered


def export_events(events: list[Any], path: str, fmt: str) -> None:
    import pandas as pd

    rows = [_to_dict(event) for event in events]
    frame = pd.DataFrame(rows)
    if fmt == "csv":
        frame.to_csv(path, index=False)
    elif fmt == "parquet":
        frame.to_parquet(path, index=False)


def detect_anomalies(
    events: list[Any], latency_field: str | None = None, required_fields: list[str] | None = None
) -> list[tuple[Any, str]]:
    anomalies: list[tuple[Any, str]] = []
    if latency_field:
        import numpy as np

        latencies = [getattr(event, latency_field, None) for event in events]
        values = [value for value in latencies if isinstance(value, (int, float))]
        if values:
            arr = np.array(values)
            threshold = arr.mean() + (3 * arr.std())
            for event in events:
                value = getattr(event, latency_field, None)
                if isinstance(value, (int, float)) and value > threshold:
                    anomalies.append((event, f"outlier {latency_field}={value}"))

    if required_fields:
        for event in events:
            data = _to_dict(event)
            for field in required_fields:
                if field not in data or data[field] in (None, ""):
                    anomalies.append((event, f"missing or empty field: {field}"))
    return anomalies


def validate_config_cmd(config_path: str) -> int:
    import jsonschema
    import yaml

    schema = {
        "type": "object",
        "properties": {
            "events": {
                "type": "object",
                "properties": {
                    "interactions_path": {"type": "string"},
                    "retrievals_path": {"type": "string"},
                    "max_events": {"type": "integer"},
                },
                "required": ["interactions_path", "retrievals_path", "max_events"],
            },
            "output": {
                "type": "object",
                "properties": {
                    "validated_events_path": {"type": "string"},
                    "summary_path": {"type": "string"},
                    "run_result_path": {"type": "string"},
                },
                "required": ["validated_events_path", "summary_path", "run_result_path"],
            },
        },
        "required": ["events", "output"],
    }
    with Path(config_path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    try:
        jsonschema.validate(instance=config, schema=schema)
        print(f"Config {config_path} is valid.")
        return 0
    except jsonschema.ValidationError as exc:
        print(f"Config {config_path} is INVALID: {exc.message}")
        return 1


def diff_contracts_cmd(old_path: str, new_path: str) -> int:
    import yaml

    def _load(path: str) -> dict[str, Any]:
        file_path = Path(path)
        with file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle) if file_path.suffix == ".json" else yaml.safe_load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"Contract payload must be a mapping: {path}")
        return payload

    old = _load(old_path)
    new = _load(new_path)
    breaking: list[str] = []

    for key in old:
        if key not in new:
            breaking.append(f"Field removed: {key}")
        elif type(old[key]) is not type(new[key]):
            breaking.append(
                f"Field type changed: {key} ({type(old[key]).__name__} -> {type(new[key]).__name__})"
            )

    for key in new:
        if key not in old:
            print(f"Field added: {key}")

    if not breaking:
        print("No breaking changes detected.")
        return 0

    print("Breaking changes detected:")
    for change in breaking:
        print(f"  {change}")
    return 1


def visualize_pipeline_cmd(config_path: str) -> int:
    import yaml

    with Path(config_path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    mermaid = [
        "graph TD",
        "    A[Interactions] --> B[Validation]",
        "    C[Retrievals] --> B[Validation]",
        "    B[Validation] --> D[Summary]",
        "    B[Validation] --> E[Validated Events]",
        f"    A -->|from| {config['events']['interactions_path']}",
        f"    C -->|from| {config['events']['retrievals_path']}",
        f"    D -->|to| {config['output']['summary_path']}",
        f"    E -->|to| {config['output']['validated_events_path']}",
    ]
    print("\n".join(mermaid))
    return 0


def coverage_report_cmd() -> int:
    print("Running pytest with coverage...")
    result = subprocess.run(
        ["pytest", "--cov=src", "--cov-report=term-missing"],
        capture_output=True,
        text=True,
        check=False,
    )
    print(result.stdout)
    print("All tests passed." if result.returncode == 0 else "Some tests failed.")
    return result.returncode


def _run_subcommand_from_argv() -> int | None:
    if len(sys.argv) <= 1:
        return None

    command = sys.argv[1]
    if command == "validate-config":
        config_path = sys.argv[2] if len(sys.argv) > 2 else "configs/base.yaml"
        return validate_config_cmd(config_path)
    if command == "diff-contracts":
        if len(sys.argv) < 4:
            print(
                "Usage: python -m llm_observability_analytics.cli.main "
                "diff-contracts <old_contract> <new_contract>"
            )
            return 2
        return diff_contracts_cmd(sys.argv[2], sys.argv[3])
    if command == "visualize-pipeline":
        config_path = sys.argv[2] if len(sys.argv) > 2 else "configs/base.yaml"
        return visualize_pipeline_cmd(config_path)
    if command == "coverage-report":
        return coverage_report_cmd()
    return None


def main() -> int:
    subcommand_exit = _run_subcommand_from_argv()
    if subcommand_exit is not None:
        return subcommand_exit

    parser = build_parser()
    args = parser.parse_args()

    if args.dry_run:
        print(f"Dry run successful. Config: {args.config}")
        return 0

    config = load_config(Path(args.config))

    if args.validate or args.filter_invalid:
        interactions, interaction_errors = load_interaction_events_with_validation(
            config.events.interactions_path, config.events.max_events
        )
        retrievals, retrieval_errors = load_retrieval_trace_events_with_validation(
            config.events.retrievals_path, config.events.max_events
        )

        if args.validate:
            if interaction_errors:
                print(f"Invalid interaction events: {len(interaction_errors)}")
                for error in interaction_errors:
                    print(f"  {error}")
            if retrieval_errors:
                print(f"Invalid retrieval events: {len(retrieval_errors)}")
                for error in retrieval_errors:
                    print(f"  {error}")

        if not args.filter_invalid and (interaction_errors or retrieval_errors):
            print("Aborting due to invalid events. Use --filter-invalid to skip them.")
            return 2
    else:
        try:
            interactions = load_interaction_events(config.events.interactions_path, config.events.max_events)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            print(f"Failed to load interaction events: {exc}")
            return 2

        try:
            retrievals = load_retrieval_trace_events(config.events.retrievals_path, config.events.max_events)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            print(f"Failed to load retrieval trace events: {exc}")
            return 2

    if args.schema or args.start_time or args.end_time or args.export_csv or args.export_parquet:
        if args.start_time or args.end_time:
            interactions = filter_events_by_time(
                interactions, args.start_time, args.end_time, ["request_timestamp"]
            )
            retrievals = filter_events_by_time(
                retrievals, args.start_time, args.end_time, ["retrieval_timestamp"]
            )

        if args.export_csv:
            interactions_csv = args.export_csv.replace(".csv", "_interactions.csv")
            retrievals_csv = args.export_csv.replace(".csv", "_retrievals.csv")
            export_events(interactions, interactions_csv, "csv")
            export_events(retrievals, retrievals_csv, "csv")
            print(f"Exported interactions and retrievals to CSV at {interactions_csv} and {retrievals_csv}")

        if args.export_parquet:
            interactions_parquet = args.export_parquet.replace(".parquet", "_interactions.parquet")
            retrievals_parquet = args.export_parquet.replace(".parquet", "_retrievals.parquet")
            export_events(interactions, interactions_parquet, "parquet")
            export_events(retrievals, retrievals_parquet, "parquet")
            print(
                "Exported interactions and retrievals to Parquet at "
                f"{interactions_parquet} and {retrievals_parquet}"
            )

        if args.schema:
            print("Detected schema for interaction events:")
            for key, value in detect_schema(interactions).items():
                print(f"  {key}: {value}")
            print("\nDetected schema for retrieval events:")
            for key, value in detect_schema(retrievals).items():
                print(f"  {key}: {value}")

    if args.detect_anomalies:
        print("Anomalies in interaction events:")
        for event, reason in detect_anomalies(
            interactions,
            latency_field="latency_ms",
            required_fields=[
                "query_id",
                "trace_id",
                "request_timestamp",
                "response_timestamp",
                "prompt_text",
                "response_text",
            ],
        ):
            print(f"  {reason}: {_to_dict(event)}")

        print("\nAnomalies in retrieval events:")
        for event, reason in detect_anomalies(
            retrievals,
            required_fields=[
                "query_id",
                "trace_id",
                "retrieval_timestamp",
                "query_text",
                "retrieval_system",
            ],
        ):
            print(f"  {reason}: {_to_dict(event)}")

    summary = {
        "interactions_loaded": len(interactions),
        "retrievals_loaded": len(retrievals),
        "interactions_path": str(config.events.interactions_path),
        "retrievals_path": str(config.events.retrievals_path),
    }

    if args.summary:
        latencies = [event.latency_ms for event in interactions if hasattr(event, "latency_ms")]
        if latencies:
            summary["interaction_latency_min_ms"] = min(latencies)
            summary["interaction_latency_max_ms"] = max(latencies)
            summary["interaction_latency_avg_ms"] = sum(latencies) / len(latencies)
        else:
            summary["interaction_latency_min_ms"] = None
            summary["interaction_latency_max_ms"] = None
            summary["interaction_latency_avg_ms"] = None

        summary["retrieval_event_count"] = len(retrievals)
        print("Event Summary Report:")
        print(f"  Interactions loaded: {summary['interactions_loaded']}")
        print(f"  Retrievals loaded: {summary['retrievals_loaded']}")
        if latencies:
            print(
                "  Interaction latency (ms): "
                f"min={summary['interaction_latency_min_ms']}, "
                f"max={summary['interaction_latency_max_ms']}, "
                f"avg={summary['interaction_latency_avg_ms']:.2f}"
            )
        else:
            print("  No interaction latency data available.")
        print("")

    try:
        config.output.summary_path.parent.mkdir(parents=True, exist_ok=True)
        with config.output.summary_path.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
    except (OSError, ValueError) as exc:
        print(f"Failed to write summary: {exc}")
        return 1

    print(f"Event processing complete. Summary written to {config.output.summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
