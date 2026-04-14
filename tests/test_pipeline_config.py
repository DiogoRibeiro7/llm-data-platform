import importlib


def test_import_pipeline_config():
    mod = importlib.import_module("llm_observability_analytics.pipeline.config")
    assert mod is not None


# TODO: add YAML loading tests and validation checks
