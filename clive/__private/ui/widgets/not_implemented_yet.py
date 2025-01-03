from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static, TabPane

from clive.__private.ui.styling import label_future_functionality
from clive.__private.ui.widgets.buttons import OneLineButton

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult
    from textual.widgets._button import ButtonVariant


class NotImplementedYetTabPane(TabPane):
    DEFAULT_CSS = """
    NotImplementedYetTabPane {
        Static {
            width: 1fr;
            text-align: center;
        }
    }
    """

    def __init__(self, title: str) -> None:
        super().__init__(title=label_future_functionality(title), disabled=True)

    def compose(self) -> ComposeResult:
        if not self._pending_children:
            yield Static("The functionality will be available soon.")


class NotImplementedYetButton(OneLineButton):
    def __init__(
        self,
        label: TextType,
        variant: ButtonVariant = "primary",
        *,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            label=label_future_functionality(label), variant=variant, id_=id_, classes=classes, disabled=True
        )
