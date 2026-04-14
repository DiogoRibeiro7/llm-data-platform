Add unit tests for `llm_observability_analytics.traces.models`.

Suggested test scope:
- Test model construction, `to_dict`/`from_dict` roundtrips and basic property behavior.
- Add tests in `tests/test_traces_models.py`.

Example:

```py
from llm_observability_analytics.traces.models import TraceRecord

def test_trace_roundtrip():
    t = TraceRecord(trace_id='t1', query_id='q1')
    d = t.to_dict()
    t2 = TraceRecord.from_dict(d)
    assert t == t2
```
