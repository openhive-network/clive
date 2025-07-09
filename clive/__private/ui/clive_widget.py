from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widget import Widget

from clive.__private.ui.clive_dom_node import CliveDOMNode

if TYPE_CHECKING:
    from textual.binding import Binding


class CliveWidget(CliveDOMNode, Widget):
    def bind(self, binding: Binding) -> None:
        """
        Bind a key to an action.

        Args:
            binding: The binding to add.
        """
        self._bindings.key_to_bindings.setdefault(binding.key, []).append(binding)
        self.refresh_bindings()

    def unbind(self, key: str) -> None:
        """Remove a key binding from this widget."""
        binding = self._bindings.key_to_bindings.pop(key, None)
        if binding:
            self.refresh_bindings()
