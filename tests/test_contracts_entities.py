import importlib


def test_import_contracts_entities():
    mod = importlib.import_module("llm_observability_analytics.contracts.entities")
    assert mod is not None


# TODO: add roundtrip dataclass tests using sample data
