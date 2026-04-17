def coverage_report_cmd() -> int:
    import subprocess
    print("Running pytest with coverage...")
    result = subprocess.run([
        "pytest", "--cov=src", "--cov-report=term-missing"
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode == 0:
        print("All tests passed.")
    else:
        print("Some tests failed.")
    return result.returncode
def visualize_pipeline_cmd(config_path: str) -> int:
    import yaml
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # Minimal pipeline: events -> validation -> summary/output
    mermaid = ["graph TD"]
    mermaid.append("    A[Interactions] --> B[Validation]")
    mermaid.append("    C[Retrievals] --> B[Validation]")
    mermaid.append("    B[Validation] --> D[Summary]")
    mermaid.append("    B[Validation] --> E[Validated Events]")
    mermaid.append(f"    A -->|from| {config['events']['interactions_path']}")
    mermaid.append(f"    C -->|from| {config['events']['retrievals_path']}")
    mermaid.append(f"    D -->|to| {config['output']['summary_path']}")
    mermaid.append(f"    E -->|to| {config['output']['validated_events_path']}")
    print("\n".join(mermaid))
    return 0
def diff_contracts_cmd(old_path: str, new_path: str) -> int:
    import json
    import yaml
    def load(path):
        if path.endswith('.json'):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    old = load(old_path)
    new = load(new_path)
    breaking = []
    for k in old:
        if k not in new:
            breaking.append(f"Field removed: {k}")
        elif type(old[k]) != type(new[k]):
            breaking.append(f"Field type changed: {k} ({type(old[k]).__name__} -> {type(new[k]).__name__})")
    for k in new:
        if k not in old:
            print(f"Field added: {k}")
    if breaking:
        print("Breaking changes detected:")
        for b in breaking:
            print(f"  {b}")
        return 1
    else:
        print("No breaking changes detected.")
        return 0
def validate_config_cmd(config_path: str) -> int:
    import yaml
    import jsonschema
    # Minimal schema for demonstration; expand as needed
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
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    try:
        jsonschema.validate(instance=config, schema=schema)
        print(f"Config {config_path} is valid.")
        return 0
    except jsonschema.ValidationError as e:
        print(f"Config {config_path} is INVALID: {e.message}")
        return 1
from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
                    parser.add_argument(
                        "--detect-anomalies",
                        action="store_true",
                        help="Detect and print events with anomalous latency or missing required fields",
                    )
                parser.add_argument(
                    "--export-csv",
                    type=str,
                    default=None,
                    help="Export filtered events to CSV at the given path (interactions and retrievals)",
                )
                parser.add_argument(
                    "--export-parquet",
                    type=str,
                    default=None,
                    help="Export filtered events to Parquet at the given path (interactions and retrievals)",
                )
            parser.add_argument(
                "--start-time",
                type=str,
                default=None,
                help="Filter events with timestamp >= this ISO8601 time (applies to request_timestamp/retrieval_timestamp)",
            )
            parser.add_argument(
                "--end-time",
                type=str,
                default=None,
                help="Filter events with timestamp <= this ISO8601 time (applies to request_timestamp/retrieval_timestamp)",
            )
        parser.add_argument(
            "--schema",
            action="store_true",
            help="Print the detected schema (fields, types, missing fields) for loaded events",
        )
    parser = argparse.ArgumentParser(prog="llm-observability")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary report of event types and basic statistics",
    )
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
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate all events and print/report any invalid records",
    )
    parser.add_argument(
        "--filter-invalid",
        action="store_true",
        help="Skip invalid events when summarizing (otherwise, loading stops at first error)",
    )
    return parser


def main() -> int:
                                    if len(sys.argv) > 1 and sys.argv[1] == "coverage-report":
                                        return coverage_report_cmd()
                                if len(sys.argv) > 1 and sys.argv[1] == "visualize-pipeline":
                                    config_path = sys.argv[2] if len(sys.argv) > 2 else "configs/base.yaml"
                                    return visualize_pipeline_cmd(config_path)
                            if len(sys.argv) > 1 and sys.argv[1] == "diff-contracts":
                                if len(sys.argv) < 4:
                                    print("Usage: python -m llm_observability_analytics.cli.main diff-contracts <old_contract> <new_contract>")
                                    return 2
                                return diff_contracts_cmd(sys.argv[2], sys.argv[3])
                        import sys
                        if len(sys.argv) > 1 and sys.argv[1] == "validate-config":
                            config_path = sys.argv[2] if len(sys.argv) > 2 else "configs/base.yaml"
                            return validate_config_cmd(config_path)
                    def detect_anomalies(events, latency_field=None, required_fields=None):
                        import numpy as np
                        anomalies = []
                        if latency_field:
                            latencies = [getattr(e, latency_field, None) for e in events]
                            latencies = [l for l in latencies if isinstance(l, (int, float))]
                            if latencies:
                                arr = np.array(latencies)
                                mean = arr.mean()
                                std = arr.std()
                                threshold = mean + 3 * std
                                for e in events:
                                    l = getattr(e, latency_field, None)
                                    if isinstance(l, (int, float)) and l > threshold:
                                        anomalies.append((e, f"outlier {latency_field}={l}"))
                        if required_fields:
                            for e in events:
                                d = e.to_dict() if hasattr(e, 'to_dict') else e
                                for f in required_fields:
                                    if f not in d or d[f] in (None, ""):
                                        anomalies.append((e, f"missing or empty field: {f}"))
                        return anomalies
                def export_events(events, path, fmt):
                    import pandas as pd
                    rows = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]
                    df = pd.DataFrame(rows)
                    if fmt == "csv":
                        df.to_csv(path, index=False)
                    elif fmt == "parquet":
                        df.to_parquet(path, index=False)

            def filter_events_by_time(events, start_time, end_time, timestamp_fields):
                from datetime import datetime
                import dateutil.parser
                if not start_time and not end_time:
                    return events
                start = dateutil.parser.isoparse(start_time) if start_time else None
                end = dateutil.parser.isoparse(end_time) if end_time else None
                filtered = []
                for e in events:
                    d = e.to_dict() if hasattr(e, 'to_dict') else e
                    for field in timestamp_fields:
                        ts = d.get(field)
                        if ts is None:
                            continue
                        if isinstance(ts, str):
                            ts_val = dateutil.parser.isoparse(ts)
                        else:
                            ts_val = ts
                        if start and ts_val < start:
                            break
                        if end and ts_val > end:
                            break
                    else:
                        filtered.append(e)
                return filtered
        def detect_schema(events):
            # Returns a dict: field -> set of types
            from collections import defaultdict
            import builtins
            schema = defaultdict(set)
            for event in events:
                if hasattr(event, 'to_dict'):
                    d = event.to_dict()
                elif isinstance(event, dict):
                    d = event
                else:
                    continue
                for k, v in d.items():
                    t = type(v).__name__ if type(v).__module__ == 'builtins' else type(v).__module__ + '.' + type(v).__name__
                    schema[k].add(t)
            return {k: sorted(list(v)) for k, v in schema.items()}

    parser = build_parser()
    args = parser.parse_args()

    if args.dry_run:
        print(f"Dry run successful. Config: {args.config}")
        return 0

    import json
    from pathlib import Path

    from llm_observability_analytics.events.loader import (
        load_interaction_events,
        load_interaction_events_with_validation,
        load_retrieval_trace_events,
        load_retrieval_trace_events_with_validation,
    )
    from llm_observability_analytics.pipeline.config import load_config

    config = load_config(Path(args.config))
    if args.schema or args.start_time or args.end_time or args.export_csv or args.export_parquet or args.detect_anomalies:
                if args.detect_anomalies:
                    print("Anomalies in interaction events:")
                    anomalies = detect_anomalies(
                        interactions,
                        latency_field="latency_ms",
                        required_fields=["query_id", "trace_id", "request_timestamp", "response_timestamp", "prompt_text", "response_text"],
                    )
                    for e, reason in anomalies:
                        print(f"  {reason}: {getattr(e, 'to_dict', lambda: e)()}")
                    print("\nAnomalies in retrieval events:")
                    anomalies = detect_anomalies(
                        retrievals,
                        latency_field=None,
                        required_fields=["query_id", "trace_id", "retrieval_timestamp", "query_text", "retrieval_system"],
                    )
                    for e, reason in anomalies:
                        print(f"  {reason}: {getattr(e, 'to_dict', lambda: e)()}")
        # Load events (interactions and retrievals)
        interactions = load_interaction_events(
            config.events.interactions_path,
            config.events.max_events,
        )
        retrievals = load_retrieval_trace_events(
            config.events.retrievals_path,
            config.events.max_events,
        )
        # Apply time filtering if requested
        if args.start_time or args.end_time:
            interactions = filter_events_by_time(
                interactions, args.start_time, args.end_time, ["request_timestamp"]
            )
            retrievals = filter_events_by_time(
                retrievals, args.start_time, args.end_time, ["retrieval_timestamp"]
            )
        if args.export_csv:
            export_events(interactions, args.export_csv.replace(".csv", "_interactions.csv"), "csv")
            export_events(retrievals, args.export_csv.replace(".csv", "_retrievals.csv"), "csv")
            print(f"Exported interactions and retrievals to CSV at {args.export_csv.replace('.csv', '_interactions.csv')} and {args.export_csv.replace('.csv', '_retrievals.csv')}")
        if args.export_parquet:
            export_events(interactions, args.export_parquet.replace(".parquet", "_interactions.parquet"), "parquet")
            export_events(retrievals, args.export_parquet.replace(".parquet", "_retrievals.parquet"), "parquet")
            print(f"Exported interactions and retrievals to Parquet at {args.export_parquet.replace('.parquet', '_interactions.parquet')} and {args.export_parquet.replace('.parquet', '_retrievals.parquet')}")
        if args.schema:
            print("Detected schema for interaction events:")
            schema = detect_schema(interactions)
            for k, v in schema.items():
                print(f"  {k}: {v}")
            print("\nDetected schema for retrieval events:")
            schema = detect_schema(retrievals)
            for k, v in schema.items():
                print(f"  {k}: {v}")
        elif not (args.export_csv or args.export_parquet):
            print(f"Filtered {len(interactions)} interaction events and {len(retrievals)} retrieval events in time range.")
        return 0

    if args.validate or args.filter_invalid:
        interactions, interaction_errors = load_interaction_events_with_validation(
            config.events.interactions_path,
            config.events.max_events,
        )
        retrievals, retrieval_errors = load_retrieval_trace_events_with_validation(
            config.events.retrievals_path,
            config.events.max_events,
        )
        if args.validate:
            if interaction_errors:
                print(f"Invalid interaction events: {len(interaction_errors)}")
                for err in interaction_errors:
                    print(f"  {err}")
            if retrieval_errors:
                print(f"Invalid retrieval events: {len(retrieval_errors)}")
                for err in retrieval_errors:
                    print(f"  {err}")
        if not args.filter_invalid and (interaction_errors or retrieval_errors):
            print("Aborting due to invalid events. Use --filter-invalid to skip them.")
            return 2
    else:
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


    # Compute summary stats if requested
    summary = {
        "interactions_loaded": len(interactions),
        "retrievals_loaded": len(retrievals),
        "interactions_path": str(config.events.interactions_path),
        "retrievals_path": str(config.events.retrievals_path),
    }
    if args.summary:
        # Interaction event stats
        latencies = [e.latency_ms for e in interactions if hasattr(e, "latency_ms")]
        if latencies:
            summary["interaction_latency_min_ms"] = min(latencies)
            summary["interaction_latency_max_ms"] = max(latencies)
            summary["interaction_latency_avg_ms"] = sum(latencies) / len(latencies)
        else:
            summary["interaction_latency_min_ms"] = None
            summary["interaction_latency_max_ms"] = None
            summary["interaction_latency_avg_ms"] = None
        # Retrieval event stats (if any timestamp/latency fields exist)
        summary["retrieval_event_count"] = len(retrievals)
        print("Event Summary Report:")
        print(f"  Interactions loaded: {summary['interactions_loaded']}")
        print(f"  Retrievals loaded: {summary['retrievals_loaded']}")
        if latencies:
            print(f"  Interaction latency (ms): min={summary['interaction_latency_min_ms']}, max={summary['interaction_latency_max_ms']}, avg={summary['interaction_latency_avg_ms']:.2f}")
        else:
            print("  No interaction latency data available.")
        print("")

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
