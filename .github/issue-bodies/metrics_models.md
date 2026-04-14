Add unit tests for `llm_observability_analytics.metrics.models`.

Suggested test scope:
- Test metric computation helpers with small inputs to assert numeric outputs (e.g., token counts, latencies, aggregates).
- Add tests verifying serialization/deserialization if present.
- Place tests in `tests/test_metrics_models.py`.

Example:

```py
from llm_observability_analytics.metrics.models import compute_metric

def test_compute_metric_simple():
    out = compute_metric([{"value": 1}, {"value": 2}])
    assert out['sum'] == 3
```
