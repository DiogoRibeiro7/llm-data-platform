from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReportSpec:
    report_name: str
    generated_for_version: str
