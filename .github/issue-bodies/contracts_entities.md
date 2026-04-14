Add unit tests for `llm_observability_analytics.contracts.entities`.

Suggested test scope:
- Validate dataclass construction, equality, and `to_dict`/`from_dict` conversions where present.
- Add tests for edge cases (missing optional fields, invalid types) using `pytest` and `tmp_path` if needed.
- Place tests in `tests/test_contracts_entities.py`.

Example skeleton:

```py
from llm_observability_analytics.contracts.entities import SomeEntity

def test_entity_roundtrip():
    e = SomeEntity(id="x", name="n")
    d = e.to_dict()
    e2 = SomeEntity.from_dict(d)
    assert e == e2
```
