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

    def bind(self, binding: Binding, before: str | None = None) -> None:
        """
        Bind a key to an action.

        Args:
        ----
        binding: The binding to add.
        before: The key of the binding to add this one before e.g.: "f2".
        """

        def add_before() -> None:
            new_bindings = {}
            for key, value in self._bindings.keys.items():
                if key == before:
                    new_bindings[binding.key] = binding
                new_bindings[key] = value

            if binding.key not in new_bindings:  # if the binding was not added before, add it now
                new_bindings[binding.key] = binding
            self._bindings.keys = new_bindings

        if before:
            add_before()
        else:
            self._bindings.keys[binding.key] = binding
        self.refresh_bindings()

    def unbind(self, key: str) -> None:
        """Remove a key binding from this widget."""
        self._bindings.keys.pop(key, None)
        self.refresh_bindings()
