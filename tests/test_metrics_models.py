import importlib


def test_import_metrics_models():
    mod = importlib.import_module("llm_observability_analytics.metrics.models")
    assert mod is not None


# TODO: add numeric helper tests with small sample inputs
