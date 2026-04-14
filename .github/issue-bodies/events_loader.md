Add unit tests for `llm_observability_analytics.events.loader`.

Suggested test scope:
- Add tests that write small `interactions.jsonl` and `retrieval.jsonl` files to `tmp_path` and assert loader functions return expected parsed objects.
- Test handling of invalid JSON lines raising `ValueError`.
- Place tests in `tests/test_events_loader.py`.

Example skeleton:

```py
from llm_observability_analytics.events.loader import load_interactions

def test_load_interactions(tmp_path):
    p = tmp_path / 'interactions.jsonl'
    p.write_text('{"query_id":"q1","trace_id":"t1"}\n')
    out = load_interactions(p)
    assert out[0].query_id == 'q1'
```
