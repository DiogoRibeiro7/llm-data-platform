import importlib


def test_import_cli_main() -> None:
    mod = importlib.import_module("llm_observability_analytics.cli.main")
    assert mod is not None


def test_build_parser_supports_expected_flags() -> None:
    mod = importlib.import_module("llm_observability_analytics.cli.main")
    parser = mod.build_parser()
    args = parser.parse_args(["--dry-run", "--config", "configs/base.yaml", "--summary"])
    assert args.dry_run is True
    assert args.summary is True
    assert args.config.endswith("base.yaml")
