import importlib


def test_import_storage_interfaces():
    mod = importlib.import_module("llm_observability_analytics.storage.interfaces")
    assert mod is not None


# TODO: add in-memory storage double tests
