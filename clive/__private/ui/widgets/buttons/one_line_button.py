from __future__ import annotations

from clive.__private.ui.widgets.buttons.clive_button import CliveButton


class OneLineButton(CliveButton):
    """Button that is without border around it, so it can be used in one line."""

    DEFAULT_CSS = """
    OneLineButton {
        border: none !important;

        &:hover {
            border: none !important;
        }
    }
    """
