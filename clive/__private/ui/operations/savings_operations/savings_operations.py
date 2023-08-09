from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Container, Grid, Horizontal
from textual.widgets import Button, Checkbox, Input, Static, TabbedContent

from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen, OperationMethods
from clive.__private.ui.operations.raw.cancel_transfer_from_savings.cancel_transfer_from_savings import (
    CancelTransferFromSavings,
)
from clive.__private.ui.widgets.account_referencing_widget import AccountReferencingWidget
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.currency_selector import CurrencySelectorLiquid
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.__private.operations.transfer_from_savings_operation import TransferFromSavingsOperation
from schemas.__private.operations.transfer_to_savings_operation import TransferToSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.storage.accounts import WorkingAccount
    from schemas.database_api.fundaments_of_reponses import SavingsWithdrawalsFundament


odd = "OddColumn"
even = "EvenColumn"


class Body(Grid):
    """Holds all places using to create transfers from/to savings."""


class RequestIdError(Exception):
    """Raise when quantity of request_ids is greater than 100."""


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
    def compose(self) -> ComposeResult:
        def get_interest_date() -> str:
            last_interest_payment = (
                self.app.world.profile_data.working_account.data.savings_hbd_last_interest_payment.replace(
                    tzinfo=None
                ).isoformat()
            )
            if last_interest_payment == "1970-01-01T00:00:00":
                return "Last interest payment: Never"
            return f"""Last interest payment: {last_interest_payment} (UTC)"""

        def get_estimated_interest() -> str:
            return (
                "Interest since last payment:"
                f" {self.app.world.profile_data.working_account.data.hbd_reward_balance.amount} HBD"
            )

        def get_interest_rate_for_hbd() -> str:
            return (
                "APR interest rate for HBD($) is"
                f" {self.app.world.node.api.database_api.get_dynamic_global_properties()['hbd_interest_rate']/100} %"
            )

        with Horizontal():
            yield SavingsBalances(self._account)
            with Container(id="interest-rate"):
                yield self.create_dynamic_label(get_interest_date, "interest-rate-date")
                yield self.create_dynamic_label(get_estimated_interest, "interest-rate-value")
                yield self.create_dynamic_label(get_interest_rate_for_hbd, "interest-rate-value-percent")


class PendingTransfer(CliveWidget):
    """class which represents one pending transfer."""

    def __init__(self, pending_transfer: SavingsWithdrawalsFundament[Asset.Hive, Asset.Hbd]):
        self.__to_account = pending_transfer.to
        self.__amount = Asset.to_legacy(pending_transfer.amount)
        self.__realized_in = pending_transfer.complete.replace(tzinfo=None).isoformat()
        self.__memo = pending_transfer.memo
        self.__request_id = str(pending_transfer.request_id)

        self.__pending_transfer = pending_transfer
        super().__init__()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static(self.__to_account, classes=odd)
            yield Static(self.__amount, classes=even)
            yield Static(str(self.__realized_in), classes=odd)
            yield Static(self.__memo, classes=even)
            yield CliveButton("Cancel", id_="delete-transfer-button", classes="delete-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete-transfer-button":
            self.app.push_screen(CancelTransferFromSavings(self.__pending_transfer))


class PendingHeader(CliveWidget):
    def compose(self) -> ComposeResult:
        yield Static("Pending transfers from savings", id="pending-title")
        with Horizontal(id="header-pending"):
            yield Static("To", classes=even)
            yield Static("Amount", classes=odd)
            yield Static("Realized on (UTC)", classes=even)
            yield Static("Memo", classes=odd)
            yield Static()


class SavingsInfo(ScrollableTabPane, CliveWidget):
    def compose(self) -> ComposeResult:
        with Container():
            working_account: WorkingAccount = self.app.world.profile_data.working_account
            pending_transfers: list[SavingsWithdrawalsFundament[Asset.Hive, Asset.Hbd]] = (
                self.app.world.node.api.database_api.find_savings_withdrawals(account=working_account.name).withdrawals
            )

            yield SavingsInterestInfo(working_account)
            if pending_transfers:
                yield PendingHeader()
                with Container(id="pending-transfers"):
                    for transfer in pending_transfers:
                        yield PendingTransfer(transfer)
            else:
                yield Static("No pending transfers from savings now !", id="without-pending-label")


class SavingsTransfers(ScrollableTabPane, OperationMethods):
    def __init__(self, title: str = "") -> None:
        super().__init__(title=title)

        self.__amount_input = Input(placeholder="put amount to transfer here", id="amount-input")
        self.__memo_input = Input(placeholder="put memo here")
        self.__to_account_input = Input(placeholder="put to-account here")
        self.__currency_selector = CurrencySelectorLiquid()

        self.__to_checkbox = Checkbox("transfer to savings", id="to-savings-choose")
        self.__from_checkbox = Checkbox("transfer from savings", id="from-savings-choose")

        self.__to_account = Horizontal(id="to-parameter")

    def compose(self) -> ComposeResult:
        yield Static("Choose type of operation", id="savings-transfer-header")
        with Horizontal(id="operation-type-choose"):
            yield self.__from_checkbox
            yield self.__to_checkbox

        yield SavingsBalances(self.app.world.profile_data.working_account, classes="transfer-savings-balances")
        with self.__to_account:
            yield Static("to", classes="label")
            yield self.__to_account_input
        with ViewBag(), Body():
            yield Static("amount", classes="label")
            yield self.__amount_input
            yield self.__currency_selector
            yield Static("memo", classes="label")
            yield self.__memo_input
        yield Static("Notice: transfer from savings will take 3 days", id="transfer-time-reminder")

    def _create_operation(
        self,
    ) -> TransferToSavingsOperation[Asset.Hive, Asset.Hbd] | TransferFromSavingsOperation[Asset.Hive, Asset.Hbd] | None:
        asset = self.__currency_selector.create_asset(self.__amount_input.value)

        if not asset:
            return None
        if self.__to_checkbox.value:
            return TransferToSavingsOperation(
                from_=self.app.world.profile_data.working_account.name,
                to=self.__to_account_input.value,
                amount=asset,
                memo=self.__memo_input.value,
            )
        elif self.__from_checkbox.value:  # noqa: RET505
            return TransferFromSavingsOperation(
                from_=self.app.world.profile_data.working_account.name,
                to=self.__to_account_input.value,
                amount=asset,
                memo=self.__memo_input.value,
                request_id=self.__create_request_id(),
            )
        else:
            self.notify("Please select type of operation")
            return None

    def __create_request_id(self) -> int:
        pending_transfers = (
            self.app.world.node.api.database_api.find_savings_withdrawals(
                account=self.app.world.profile_data.working_account.name
            ).withdrawals,
        )
        max_number_of_request_ids: Final[int] = 100

        if not pending_transfers[0]:
            return 0

        if len(pending_transfers) >= max_number_of_request_ids:
            raise RequestIdError("Maximum quantity of request ids is 100")

        sorted_transfers = sorted(pending_transfers[0], key=lambda x: x.request_id)
        last_occupied_id = sorted_transfers[-1].request_id

        return last_occupied_id + 1


class Savings(OperationBaseScreen):
    def create_left_panel(self) -> ComposeResult:
        with TabbedContent():
            yield SavingsInfo("savings info")
            yield SavingsTransfers("transfer")

    @on(Checkbox.Changed)
    def checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.value:
            _check_boxes = self.query(Checkbox)

            for check_box in _check_boxes.filter(".-on"):
                if check_box != event.checkbox:
                    check_box.value = False
                    break
