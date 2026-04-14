from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SplitAssignment:
    record_id: str
    split: str
