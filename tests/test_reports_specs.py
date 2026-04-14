import importlib


def test_import_reports_specs():
    mod = importlib.import_module("llm_observability_analytics.reports.specs")
    assert mod is not None


# TODO: add spec generation unit tests
