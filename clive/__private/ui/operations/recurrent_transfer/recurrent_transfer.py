from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError
from textual.binding import Binding
from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.currency_selector_liquid.currency_selector_liquid import CurrencySelectorLiquid
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import RecurrentTransferOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class AdditionalPlaceTaker(Static):
    """Container used for making correct layout of extensions and recurrence"""


class RecurrentTransfer(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "add_to_cart", "Add to cart"),
        Binding("f5", "fast_broadcast", "Fast broadcast"),
        Binding("f10", "finalize", "Finalize transaction"),
    ]

    def __init__(self) -> None:
        super().__init__()

        self.__to_input = Input(placeholder="e.g.: some-account")
        self.__amount_input = Input(placeholder="e.g.: 5.000")
        self.__memo_input = Input(placeholder="e.g.: For the coffee!")
        self.__recurrence_input = Input(placeholder="e.g.: 26. Notice: default value is 0")
        self.__executions_input = Input(placeholder="e.g.: 3. Notice: default value is 0")
        self.__currency_selector = CurrencySelectorLiquid()

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Recurrent transfer")
            with Body():
                yield Static("from", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="from-label")
                yield PlaceTaker()
                yield Static("to", classes="label")
                yield self.__to_input
                yield Static("amount", classes="label")
                yield self.__amount_input
                yield self.__currency_selector
                yield Static("memo", classes="label")
                yield self.__memo_input
                yield AdditionalPlaceTaker()
                yield Static("recurrence", classes="label")
                yield self.__recurrence_input
                yield Static("executions", classes="label")
                yield self.__executions_input

    def create_operation(self) -> Operation | None:
        try:
            if self.__executions_input.value and self.__recurrence_input.value:
                return RecurrentTransferOperation(
                    from_=str(self.app.world.profile_data.name),
                    to=self.__to_input.value,
                    amount=self.__currency_selector.selected.value(float(self.__amount_input.value)),
                    memo=self.__memo_input.value,
                    recurrence=int(self.__recurrence_input.value),
                    executions=int(self.__executions_input.value),
                )
            elif self.__executions_input.value or self.__recurrence_input.value:  # noqa: RET505
                return (
                    RecurrentTransferOperation(
                        from_=str(self.app.world.profile_data.name),
                        to=self.__to_input.value,
                        amount=self.__currency_selector.selected.value(float(self.__amount_input.value)),
                        memo=self.__memo_input.value,
                        recurrence=int(self.__recurrence_input.value),
                    )
                    if self.__recurrence_input.value
                    else RecurrentTransferOperation(
                        from_=str(self.app.world.profile_data.name),
                        to=self.__to_input.value,
                        amount=self.__currency_selector.selected.value(float(self.__amount_input.value)),
                        memo=self.__memo_input.value,
                        executions=int(self.__executions_input.value),
                    )
                )
            return RecurrentTransferOperation(  # noqa: TRY300
                from_=str(self.app.world.profile_data.name),
                to=self.__to_input.value,
                amount=self.__currency_selector.selected.value(float(self.__amount_input.value)),
                memo=self.__memo_input.value,
            )

        except ValidationError as error:
            Notification(f"Operation failed the validation process.\n{error}", category="error").show()
            return None
