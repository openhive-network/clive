from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widget import Widget

from clive.__private.ui.clive_dom_node import CliveDOMNode

if TYPE_CHECKING:
    from textual.binding import Binding

    from clive.__private.core.app_state import AppState
    from clive.__private.core.commands.commands import TUICommands
    from clive.__private.core.node import Node
    from clive.__private.core.profile import Profile
    from clive.__private.core.world import TUIWorld


class CliveWidget(CliveDOMNode, Widget):
    """
    An ordinary textual widget that also knows what type of application it belongs to.

    Inspired by: https://github.com/Textualize/textual/discussions/1099#discussioncomment-4049612
    """

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

    def bind(self, binding: Binding) -> None:
        """
        Bind a key to an action.

        Args:
        ----
            binding: The binding to add.
        """
        self._bindings.key_to_bindings.setdefault(binding.key, []).append(binding)
        self.refresh_bindings()

    def unbind(self, key: str) -> None:
        """Remove a key binding from this widget."""
        binding = self._bindings.key_to_bindings.pop(key, None)
        if binding:
            self.refresh_bindings()
