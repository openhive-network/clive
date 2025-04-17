from __future__ import annotations

from clive.__private.core.constants.tui.themes import DEFAULT_THEME
from clive.__private.storage.migrations import v1


class ProfileStorageModel(v1.ProfileStorageModel):
    tui_theme: str = DEFAULT_THEME

    @staticmethod
    def upgrade(old: v1.ProfileStorageModel) -> ProfileStorageModel:  # type: ignore[override]  # should always take previous model
        return ProfileStorageModel(tui_theme=DEFAULT_THEME, **old.dict())
