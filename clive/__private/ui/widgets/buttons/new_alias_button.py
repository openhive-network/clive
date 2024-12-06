from __future__ import annotations

from clive.__private.core.constants.tui.bindings import NEW_ALIAS_BINDING_KEY
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class NewKeyAliasButton(CliveButton):
    DEFAULT_CSS = """
        NewKeyAliasButton {
            width: 25;
        }
        """

    class Pressed(CliveButton.Pressed):
        """Message send when NewAliasButton is pressed."""

    def __init__(self) -> None:
        super().__init__(f"New alias ({NEW_ALIAS_BINDING_KEY.upper()})", id_="new-alias-button", variant="success")


class NewKeyAliasOneLineButton(OneLineButton, NewKeyAliasButton):
    class Pressed(NewKeyAliasButton.Pressed):
        """Used to identify exactly that NewAliasOneLineButton was pressed."""
