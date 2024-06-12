from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.widgets.clive_button import CliveButton
from clive.models import Asset

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput


class GenerousButton(CliveButton):
    """Button that fill the related input with the entire selected asset balance."""

    DEFAULT_CSS = """
    GenerousButton {
        min-width: 14;
        width: 14;
    }
    """

    def __init__(
        self,
        related_input: CliveValidatedInput[Asset.AnyT],
        amount_callback: Callable[[], Asset.AnyT],
        *,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(label="All!", variant="success", id_=id_, classes=classes)
        self._related_input = related_input
        self._amount_callback = amount_callback

    @on(CliveButton.Pressed)
    def fill_input_by_all(self) -> None:
        """If the balance is not 0, fill the related input with the entire selected asset balance."""
        if int(self._amount_callback().amount) == 0:
            self.notify("Zero is not a enough value to perform this action", severity="warning")
            return

        self._related_input.input.value = Asset.pretty_amount(self._amount_callback())
