from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal
from textual.widgets import Button, Static, TabbedContent, TabPane

from clive.__private.ui.operations.raw.cancel_transfer_from_savings.cancel_transfer_from_savings import (
    CancelTransferFromSavings,
)
from clive.__private.ui.operations.savings_operation_base_screen import SavingOperationBaseScreen
from clive.__private.ui.widgets.account_referencing_widget import AccountReferencingWidget
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.models import Asset

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
    from schemas.database_api.fundaments_of_reponses import SavingsWithdrawalsFundament


odd = "OddColumn"
even = "EvenColumn"


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
        self.__request_id = pending_transfer.request_id
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
            self.app.push_screen(CancelTransferFromSavings())


class PendingHeader(CliveWidget):
    def compose(self) -> ComposeResult:
        yield Static("Pending transfers from savings", id="pending-title")
        with Horizontal(id="header-pending"):
            yield Static("To", classes=even)
            yield Static("Amount", classes=odd)
            yield Static("Realized on (UTC)", classes=even)
            yield Static("Memo", classes=odd)
            yield Static()


class Savings(SavingOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

    def create_left_panel(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("savings info"), Container():
                yield SavingsInterestInfo(self.app.world.profile_data.working_account)
                pending_transfers = self.app.world.node.api.database_api.find_savings_withdrawals(
                    account=self.app.world.profile_data.working_account.name
                ).withdrawals
                if pending_transfers:
                    yield PendingHeader()
                    with Container(id="pending-transfers"):
                        for transfer in pending_transfers:
                            yield PendingTransfer(transfer)

                else:
                    yield Static("No pending transfers from savings now !", id="without-pending-label")
            with TabPane("transfer"):
                yield Static("NOT IMPLEMENTED YET")

    def summary_of_operation(self) -> RawOperationBaseScreen | None:
        return None
