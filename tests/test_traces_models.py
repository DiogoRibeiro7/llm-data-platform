import importlib


def test_import_traces_models():
    mod = importlib.import_module("llm_observability_analytics.traces.models")
    assert mod is not None


# TODO: add roundtrip tests for TraceRecord
