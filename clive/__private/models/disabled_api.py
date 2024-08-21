from __future__ import annotations

from dataclasses import dataclass

from clive.__private.core.formatters.data_labels import MISSING_API_LABEL


@dataclass(kw_only=True)
class DisabledAPI:
    missing_api: str

    @property
    def missing_api_text(self) -> str:
        return f"{MISSING_API_LABEL} (missing {self.missing_api})"
