Add unit tests for `llm_observability_analytics.storage.interfaces`.

Suggested test scope:
- Test base storage interface behavior using a small in-memory or temp-backed test double.
- Verify method signatures (write/read) and expected exceptions on unsupported operations.
- Place tests in `tests/test_storage_interfaces.py`.

Example:

```py
from llm_observability_analytics.storage.interfaces import StorageInterface

class DummyStorage(StorageInterface):
    def write(self, *a, **k):
        return True

def test_storage_interface():
    d = DummyStorage()
    assert d.write('x') is True
```
