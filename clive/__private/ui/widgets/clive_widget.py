from __future__ import annotations

import typing
from typing import TYPE_CHECKING

from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import Footer

if TYPE_CHECKING:
    from textual.binding import Binding

    from clive.__private.ui.app import Clive


class CliveWidget(Widget):
    """
    An ordinary textual widget that also knows what type of application it belongs to.

    Inspired by: https://github.com/Textualize/textual/discussions/1099#discussioncomment-4049612
    """

    @property
    def app(self) -> Clive:  # type: ignore[override]
        from clive.__private.ui.app import Clive  # To avoid circular imports

        return typing.cast(Clive, super().app)

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
        self._refresh_footer_bindings()

    def unbind(self, key: str) -> None:
        """Remove a key binding from this widget."""
        self._bindings.keys.pop(key, None)
        self._refresh_footer_bindings()

    def _refresh_footer_bindings(self) -> None:
        try:
            footer = self.app.query_one(Footer)
        except NoMatches:
            return

        footer._key_text = None  # needs to be set to None, otherwise the footer won't update bindings on refresh()
        footer.refresh()
