import importlib


def test_import_cli_main():
    mod = importlib.import_module("llm_observability_analytics.cli.main")
    assert mod is not None


# TODO: add tests for --help, --dry-run and config loading using tmp_path
