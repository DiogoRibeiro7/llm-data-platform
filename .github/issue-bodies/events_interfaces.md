Add unit tests for `llm_observability_analytics.events.interfaces`.

Suggested test scope:
- Verify abstract base classes raise `NotImplementedError` for abstract methods when instantiated improperly.
- Provide a small test double implementing the interface and assert it satisfies the expected call signatures.
- Add tests in `tests/test_events_interfaces.py`.

Example:

```py
from llm_observability_analytics.events.interfaces import BaseLoader

class Dummy(BaseLoader):
    def load(self, *a, **k):
        return []

def test_loader_interface():
    d = Dummy()
    assert hasattr(d, 'load')
```
