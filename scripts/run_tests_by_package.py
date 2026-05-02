#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def collect_tests(tests_dir: Path):
    pattern = re.compile(r"from\s+(llm_[a-z0-9_]+)|import\s+(llm_[a-z0-9_]+)")
    groups = defaultdict(list)
    for p in sorted(tests_dir.glob("test_*.py")):
        text = p.read_text(encoding="utf-8")
        m = pattern.search(text)
        if m:
            pkg = m.group(1) or m.group(2)
            groups[pkg].append(str(p))
        else:
            groups["__root__"].append(str(p))
    return groups


def run_group(pkg: str, files: list[str], src_path: Path) -> int:
    print(f"\n=== Running tests for: {pkg} ({len(files)} files) ===")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_path)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--strict-markers",
        "--disable-warnings",
        "-o",
        "addopts=",
    ]
    if pkg != "__root__":
        cmd.extend(["--cov", pkg, "--cov-report", "term-missing"])
    cmd.extend(files)
    proc = subprocess.run(cmd, env=env)
    return proc.returncode


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    tests_dir = repo_root / "tests"
    src_dir = repo_root / "src"
    if not tests_dir.exists():
        print("No tests directory found.")
        return 0

    groups = collect_tests(tests_dir)
    exit_code = 0
    for pkg, files in groups.items():
        code = run_group(pkg, files, src_dir)
        if code != 0:
            exit_code = code

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
