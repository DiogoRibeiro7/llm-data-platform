Add unit tests for `llm_observability_analytics.reports.specs`.

Suggested test scope:
- Test spec generation functions produce expected dict structures for small inputs.
- Add tests for edge cases (empty inputs, missing optional fields).
- Place tests in `tests/test_reports_specs.py`.

Example:

```py
from llm_observability_analytics.reports.specs import build_spec

def test_build_spec_simple():
    spec = build_spec([])
    assert isinstance(spec, dict)
```
