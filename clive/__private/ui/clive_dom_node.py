from __future__ import annotations

from typing import TYPE_CHECKING, cast

from textual.dom import DOMNode

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState
    from clive.__private.core.commands.commands import TUICommands
    from clive.__private.core.node import Node
    from clive.__private.core.profile import Profile
    from clive.__private.core.world import TUIWorld
    from clive.__private.ui.app import Clive
    from clive.__private.ui.bindings import CliveBindings


class CliveDOMNode(DOMNode):
    """
    An ordinary textual DOMNode that also knows what type of application it belongs to.

    Inspired by: https://github.com/Textualize/textual/discussions/1099#discussioncomment-4049612
    """

    @property
    def app(self) -> Clive:  # type: ignore[override]
        return cast("Clive", super().app)

    @property
    def world(self) -> TUIWorld:
        return self.app.world

    @property
    def profile(self) -> Profile:
        return self.world.profile

    @property
    def app_state(self) -> AppState:
        return self.world.app_state

    @property
    def commands(self) -> TUICommands:
        return self.world.commands

    @property
    def node(self) -> Node:
        return self.world.node

    @property
    def custom_bindings(self) -> CliveBindings:
        return self.app.custom_bindings
