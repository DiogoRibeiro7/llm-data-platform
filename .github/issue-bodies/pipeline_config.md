Add unit tests for `llm_observability_analytics.pipeline.config`.

Suggested test scope:
- Test loading YAML config files with minimal settings and assert defaults are applied.
- Validate config validation raises on missing required fields.
- Place tests in `tests/test_pipeline_config.py`.

Example:

```py
from llm_observability_analytics.pipeline.config import load_config

def test_load_default(tmp_path):
    cfg = tmp_path / 'c.yaml'
    cfg.write_text('model: test')
    conf = load_config(cfg)
    assert conf['model'] == 'test'
```
