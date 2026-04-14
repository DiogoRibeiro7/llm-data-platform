Add unit tests for `llm_observability_analytics.cli.main`.

Suggested test scope:
- Verify `--help` and `--dry-run` return exit code 0.
- Run the CLI with a minimal `configs/base.yaml` using `tmp_path` and assert no exceptions.
- Mock file loading and validate expected calls (`monkeypatch` or `unittest.mock`).
- Add tests in `tests/test_cli_main.py` using `subprocess.run` or calling the module entrypoint.

Example test skeleton:

```py
import subprocess, sys

def test_cli_dry_run(tmp_path):
    cfg = tmp_path / "configs" / "base.yaml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("model: test")
    res = subprocess.run([sys.executable, "-m", "llm_observability_analytics.cli.main", "--dry-run", "--config", str(cfg)])
    assert res.returncode == 0
```
