from __future__ import annotations

from typing import Self

from clive.__private.core.constants.tui.themes import DEFAULT_THEME
from clive.__private.storage.migrations import v1


class ProfileStorageModel(v1.ProfileStorageModel):
    tui_theme: str = DEFAULT_THEME

    @classmethod
    def upgrade(cls, old: v1.ProfileStorageModel) -> Self:  # type: ignore[override]  # should always take previous model
        return cls(**old.dict())
