from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QualityCheckResult:
    check_name: str
    passed: bool
    message: str
