from __future__ import annotations

from textual.message import Message


class NodeDataUpdated(Message):
    """Emitted when app.node_data has been updated"""


class ProfileDataUpdated(Message):
    def __init__(self) -> None:
        super().__init__()

    """Emitted when app.profile_data has been updated"""


class AppStateUpdated(Message):
    """Emitted when app.app_state has been updated"""
