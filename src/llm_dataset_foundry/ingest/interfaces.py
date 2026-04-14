from __future__ import annotations

from abc import ABC, abstractmethod


class SourceAdapter(ABC):
    @abstractmethod
    def read(self) -> list[dict[str, object]]:
        """Read source records from an upstream repository artifact."""
