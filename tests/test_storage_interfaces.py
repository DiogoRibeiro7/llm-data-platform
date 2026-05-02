from __future__ import annotations

import pytest

from llm_observability_analytics.storage.interfaces import EventStore


def test_event_store_is_abstract() -> None:
    with pytest.raises(TypeError):
        EventStore()


def test_event_store_in_memory_double_records_payloads() -> None:
    class InMemoryStore(EventStore):
        def __init__(self) -> None:
            self.rows: list[dict[str, object]] = []

        def write(self, payload: dict[str, object]) -> None:
            self.rows.append(payload)

    store = InMemoryStore()
    store.write({"event": "interaction", "count": 1})
    store.write({"event": "retrieval", "count": 2})

    assert store.rows == [
        {"event": "interaction", "count": 1},
        {"event": "retrieval", "count": 2},
    ]
