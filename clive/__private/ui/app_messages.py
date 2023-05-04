from __future__ import annotations

from typing import TYPE_CHECKING

from textual.message import Message

if TYPE_CHECKING:
    from clive.__private.core.profile_data import ProfileData


class NodeDataUpdated(Message):
    """Emitted when app.node_data has been updated"""


class ProfileDataUpdated(Message):
    def __init__(self, password: str | None = None, profile_data: ProfileData | None = None) -> None:
        self.password = password
        self.profile_data = profile_data
        super().__init__()

    """Emitted when app.profile_data has been updated"""


class AppStateUpdated(Message):
    """Emitted when app.app_state has been updated"""
