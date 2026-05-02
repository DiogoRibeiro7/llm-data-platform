from pathlib import Path

import pytest

from llm_observability_analytics.pipeline.config import load_config


def test_load_config_resolves_relative_paths(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
events:
  interactions_path: data/interactions.jsonl
  retrievals_path: data/retrievals.jsonl
  max_events: 25
output:
  validated_events_path: out/validated.jsonl
  summary_path: out/summary.json
  run_result_path: out/result.json
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.events.max_events == 25
    assert config.events.interactions_path == tmp_path / "data" / "interactions.jsonl"
    assert config.events.retrievals_path == tmp_path / "data" / "retrievals.jsonl"
    assert config.output.summary_path == tmp_path / "out" / "summary.json"


def test_load_config_rejects_non_mapping(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="Config payload must be a mapping"):
        load_config(config_path)


def test_load_config_rejects_invalid_max_events(tmp_path: Path) -> None:
    config_path = tmp_path / "bad_max.yaml"
    config_path.write_text(
        """
events:
  interactions_path: interactions.jsonl
  retrievals_path: retrievals.jsonl
  max_events: 0
output:
  validated_events_path: validated.jsonl
  summary_path: summary.json
  run_result_path: result.json
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="events.max_events must be > 0"):
        load_config(config_path)
