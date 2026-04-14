import importlib


def test_import_events_loader():
    mod = importlib.import_module("llm_observability_analytics.events.loader")
    assert mod is not None


# TODO: add file-based loader tests using tmp_path
