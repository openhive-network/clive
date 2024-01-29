from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Container, Grid, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Button, Label, LoadingIndicator, RadioSet, Static, TabPane

from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.data_providers.savings_data_provider import SavingsDataProvider
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.bindings import CartBinding, OperationActionBindings
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.operations.raw.cancel_transfer_from_savings.cancel_transfer_from_savings import (
    CancelTransferFromSavings,
)
from clive.__private.ui.widgets.account_referencing_widget import AccountReferencingWidget
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_radio_button import CliveRadioButton
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.asset_amount_input import AssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.notice import Notice
from clive.exceptions import RequestIdError
from clive.models import Asset
from schemas.operations import (
    CancelTransferFromSavingsOperation,
    TransferFromSavingsOperation,
    TransferToSavingsOperation,
)

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
    from clive.models.aliased import SavingsWithdrawals


odd = "OddColumn"
even = "EvenColumn"


class ScrollablePart(ScrollableContainer, can_focus=False):
    pass


class Body(Grid):
    """Holds all places using to create transfers from/to savings."""


class SavingsBalances(AccountReferencingWidget):
    """class used to displays HBD/HIVE savings balances."""

    def compose(self) -> ComposeResult:
        yield Static("SAVINGS BALANCE", id="savings-title")
        yield Static("HIVE", id="savings-token-hive")
        yield Static("HBD", id="savings-token-hbd")
        yield self.create_dynamic_label(
            lambda: Asset.pretty_amount(self._account.data.hive_savings), "savings-value-hive"
        )
        yield self.create_dynamic_label(
            lambda: Asset.pretty_amount(self._account.data.hbd_savings), "savings-value-hbd"
        )


class SavingsInterestInfo(AccountReferencingWidget):
    def __init__(self) -> None:
        super().__init__(account=self.app.world.profile_data.working_account)

        self.interest_container = Container(id="interest-rate")

    @property
    def provider(self) -> SavingsDataProvider:
        return self.app.query_one(SavingsDataProvider)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield SavingsBalances(self._account)
            with self.interest_container:
                yield LoadingIndicator()

    def on_mount(self) -> None:
        self.watch(self.provider, "_content", callback=self.sync_data)

    def sync_data(self, content: SavingsData) -> None:
        if not self.provider.is_content_set:
            return

        def get_interest_date() -> str:
            last_interest_payment = humanize_datetime(content.last_interest_payment)
            return f"""Last interest payment: {last_interest_payment} (UTC)"""

        def get_estimated_interest() -> str:
            return f"Interest since last payment: {self._account.data.hbd_unclaimed.amount} HBD"

        def get_interest_rate_for_hbd() -> str:
            return f"APR interest rate for HBD($) is {content.hbd_interest_rate / 100}%"

        with self.app.batch_update():
            self.interest_container.query("*").remove()
            self.interest_container.mount_all(
                [
                    self.create_dynamic_label(get_interest_date, "interest-rate-date"),
                    self.create_dynamic_label(get_estimated_interest, "interest-rate-value"),
                    self.create_dynamic_label(get_interest_rate_for_hbd, "interest-rate-value-percent"),
                ]
            )


class PendingTransfer(CliveWidget):
    """class which represents one pending transfer."""

    def __init__(self, transfer: SavingsWithdrawals):
        super().__init__()
        self.__transfer = transfer

    def compose(self) -> ComposeResult:
        yield Label(self.__transfer.to, classes=odd)
        yield Label(Asset.to_legacy(self.__transfer.amount), classes=even)
        yield Label(str(self.__realized_on), classes=odd)
        yield Label(self.__transfer.memo, classes=even)
        yield CliveButton("Cancel", id_="delete-transfer-button")

    @property
    def __realized_on(self) -> str:
        return humanize_datetime(self.__transfer.complete)

    @on(Button.Pressed, "#delete-transfer-button")
    def move_to_cancel_transfer(self) -> None:
        if (
            CancelTransferFromSavingsOperation(from_=self.__transfer.from_, request_id=self.__transfer.request_id)
            in self.app.world.profile_data.cart
        ):
            self.notify("The operation is already in the cart!", severity="error")
            return
        self.app.push_screen(CancelTransferFromSavings(self.__transfer))


class PendingHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("To", classes=even)
        yield Label("Amount", classes=odd)
        yield Label("Realized on (UTC)", classes=even)
        yield Label("Memo", classes=odd)
        yield Label()


class PendingTransfers(Vertical):
    @property
    def provider(self) -> SavingsDataProvider:
        return self.app.query_one(SavingsDataProvider)

    def compose(self) -> ComposeResult:
        yield LoadingIndicator()

    def on_mount(self) -> None:
        self.watch(self.provider, "_content", callback=self.__sync_pending_transfers)

    def __sync_pending_transfers(self, content: SavingsData) -> None:
        if not self.provider.is_content_set:
            return

        pending_transfers = content.pending_transfers
        if not pending_transfers:
            with self.app.batch_update():
                self.query("*").remove()
                self.mount(Static("No transfers from savings now", classes="number-of-transfers"))
            return

        things_to_mount = [
            Static(f"Number of transfers from savings now: {len(pending_transfers)}", classes="number-of-transfers"),
            PendingHeader(),
            ScrollablePart(
                *[PendingTransfer(transfer) for transfer in pending_transfers],
            ),
        ]

        with self.app.batch_update():
            self.query("*").remove()
            self.mount_all(things_to_mount)


class SavingsInfo(TabPane, CliveWidget):
    def compose(self) -> ComposeResult:
        yield SavingsInterestInfo()
        yield PendingTransfers()


class SavingsTransfers(TabPane, OperationActionBindings):
    def __init__(self, title: TextType) -> None:
        super().__init__(title=title)

        self.__amount_input = AssetAmountInput()
        self.__memo_input = MemoInput()
        self.__to_account_input = AccountNameInput(value=self.app.world.profile_data.working_account.name)

        self.__to_button = CliveRadioButton("transfer to savings", id="to-savings-choose", value=True)
        self.__from_button = CliveRadioButton("transfer from savings", id="from-savings-choose")

        self.__transfer_time_reminder = Notice("transfer from savings will take 3 days")
        self.__transfer_time_reminder.visible = False

    def compose(self) -> ComposeResult:
        yield Static("Choose type of operation", id="savings-transfer-header")
        with RadioSet(id="operation-type-choose"):
            yield self.__to_button
            yield self.__from_button

        yield SavingsBalances(self.app.world.profile_data.working_account, classes="transfer-savings-balances")
        yield self.__transfer_time_reminder
        with ScrollablePart(), Body():
            yield from self.__to_account_input.compose()
            yield from self.__amount_input.compose()
            yield from self.__memo_input.compose()

    @on(RadioSet.Changed)
    def visibility_of_transfer_time_reminder(self, event: RadioSet.Changed) -> None:
        if event.radio_set.pressed_button.id == "from-savings-choose":  # type: ignore[union-attr]
            self.__transfer_time_reminder.visible = True
            return
        self.__transfer_time_reminder.visible = False

    def _create_operation(
        self,
    ) -> TransferToSavingsOperation | TransferFromSavingsOperation | None:
        asset = self.__amount_input.value

        if not asset:
            return None

        to = self.__to_account_input.value
        if not to:
            return None

        if self.__to_button.value:
            return TransferToSavingsOperation(
                from_=self.app.world.profile_data.working_account.name,
                to=to,
                amount=asset,
                memo=self.__memo_input.value,
            )

        try:
            request_id = self.__create_request_id()
        except RequestIdError as error:
            self.notify(str(error), severity="error")
            return None

        return TransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=to,
            amount=asset,
            memo=self.__memo_input.value,
            request_id=request_id,
        )

    def __create_request_id(self) -> int:
        provider = self.app.query_one(SavingsDataProvider)
        savings_data = provider.content

        transfer_from_savings_operations_in_cart = [
            operation
            for operation in self.app.world.profile_data.cart
            if isinstance(operation, TransferFromSavingsOperation)
        ]
        return savings_data.create_request_id(future_transfers=transfer_from_savings_operations_in_cart)


class Savings(OperationBaseScreen, CartBinding):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Savings operations")
        with SavingsDataProvider(), CliveTabbedContent():
            yield SavingsInfo(title="savings info")
            yield SavingsTransfers(title="transfer")
