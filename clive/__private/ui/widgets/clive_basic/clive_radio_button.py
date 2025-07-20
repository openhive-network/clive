from __future__ import annotations

from textual.widgets import RadioButton


class CliveRadioButton(RadioButton):
    """
    Due to bug in Ubuntu we have to replace icon of the RadioButton by simple 'O'.

    Attributes:
        BUTTON_INNER: The inner content of the radio button, which is a simple 'O'.
    """

    BUTTON_INNER = "O"
