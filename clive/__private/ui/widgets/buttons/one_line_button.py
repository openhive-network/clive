from __future__ import annotations

from clive.__private.ui.widgets.buttons.clive_button import CliveButton


class OneLineButton(CliveButton):
    """
    Button that is without border around it, so it can be used in one line.

    Attributes:
        DEFAULT_CSS: Default CSS styles for the OneLineButton.
    """

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that OneLineButton was pressed."""

    DEFAULT_CSS = """
    OneLineButton {
        border: none !important;

        &:hover {
            border: none !important;
        }
    }
    """


class OneLineButtonUnfocusable(OneLineButton, can_focus=False):
    """Unfocusable version of `OneLineButton`."""

    class Pressed(OneLineButton.Pressed):
        """Used to identify exactly that OneLineButtonUnfocusable was pressed."""
