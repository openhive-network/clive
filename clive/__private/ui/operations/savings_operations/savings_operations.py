from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

from textual import work
from textual.containers import Container, Grid, Horizontal, ScrollableContainer
from textual.reactive import var
from textual.widgets import Button, RadioButton, RadioSet, Static, TabbedContent

from clive.__private.config import settings
from clive.__private.logger import logger
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen, OperationMethods
from clive.__private.ui.operations.raw.cancel_transfer_from_savings.cancel_transfer_from_savings import (
    CancelTransferFromSavings,
)
from clive.__private.ui.widgets.account_referencing_widget import AccountReferencingWidget
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.asset_amount_input import AssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.__private.operations.transfer_from_savings_operation import TransferFromSavingsOperation
from schemas.__private.operations.transfer_to_savings_operation import TransferToSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.storage.accounts import WorkingAccount
    from schemas.database_api.fundaments_of_reponses import SavingsWithdrawalsFundament


@dataclass
class SavingsData:
    pending_transfers: Any = None
    hbd_interest_rate: Any = None
    last_interest_payment: Any = None


class GetSavingsInformation(CliveWidget):

    content = var(None)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__information = SavingsData()
        self.set_interval(settings.get("node.refresh_rate", 1.5), lambda: self.on_data_refresh())  # type: ignore
    #
    # @property
    # def content(self) -> Any:
    #     return self.__information

    async def on_data_refresh(self) -> None:
        self._update_savings_data()
        self.content = self.__information
        logger.debug(f"GetSavingsInformation {self.content}")

    def update(self) -> None:
        self._update_savings_data()

    @work(name="savings data update worker")
    async def _update_savings_data(self) -> None:
        working_account_name = self.app.world.profile_data.working_account.name

        gdpo = await self.app.world.app_state.get_dynamic_global_properties()
        response_db_api = await self.app.world.node.api.database_api.find_accounts(accounts=[working_account_name])
        pending_transfers = await self.app.world.node.api.database_api.find_savings_withdrawals(
            account=working_account_name
        )

        self.__information.hbd_interest_rate = gdpo.hbd_interest_rate
        self.__information.last_interest_payment = response_db_api.accounts[0].hbd_last_interest_payment
        self.__information.pending_transfers = pending_transfers.withdrawals


odd = "OddColumn"
even = "EvenColumn"


class PlaceTaker(Static):
    """Using to ensure valid display of the grid."""


class CliveRadioButton(RadioButton):
    """Due to bug in Ubuntu we have to replace icon of the RadioButton by simple 'O'."""

    BUTTON_INNER = "O"


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = GetSavingsInformation()

    def compose(self) -> ComposeResult:
        def get_interest_date() -> str:
            last_interest_payment = self.provider.content.last_interest_payment
            if last_interest_payment is None:
                return "Last interest payment: Never"
            return f"""Last interest payment: {last_interest_payment} (UTC)"""

        def get_estimated_interest() -> str:
            return (
                "Interest since last payment:"
                f" {self.app.world.profile_data.working_account.data.hbd_unclaimed.amount} HBD"
            )

        def get_interest_rate_for_hbd() -> str:
            return f"APR interest rate for HBD($) is {self.provider.content.hbd_interest_rate}%"

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


class PendingTransfers(ScrollableContainer, CliveWidget):
    def compose(self) -> ComposeResult:
        pending_transfers: list[SavingsWithdrawalsFundament[Asset.Hive, Asset.Hbd]] = (
            self.__provider.content.pending_transfers
        )
        if pending_transfers:
            with ScrollableContainer(id="pending-transfers"):
                for transfer in pending_transfers:
                    yield PendingTransfer(transfer)
                yield Static()
        else:
            yield Static("Now pending transfers from savings now !", id="without-pending-label")


class SavingsInfo(ScrollableTabPane, CliveWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__provider = GetSavingsInformation()


    def on_mount(self) -> None:
        self.watch(self.__provider, "trigger", self.rebuild_pending_transfers)

    def compose(self) -> ComposeResult:
        with Container():
            working_account: WorkingAccount = self.app.world.profile_data.working_account
            yield SavingsInterestInfo(working_account)
            yield PendingTransfers()


class SavingsTransfers(ScrollableTabPane, OperationMethods):
    def __init__(self, title: str = "") -> None:
        super().__init__(title=title)
        self.provider = GetSavingsInformation()

        self.__amount_input = AssetAmountInput()
        self.__memo_input = MemoInput()
        self.__to_account_input = AccountNameInput(value=self.app.world.profile_data.working_account.name)

        self.__to_button = CliveRadioButton("transfer to savings", id="to-savings-choose")
        self.__from_button = CliveRadioButton("transfer from savings", id="from-savings-choose")

    def compose(self) -> ComposeResult:
        yield Static("Choose type of operation", id="savings-transfer-header")
        with RadioSet(id="operation-type-choose"):
            yield self.__from_button
            yield self.__to_button

        yield SavingsBalances(self.app.world.profile_data.working_account, classes="transfer-savings-balances")
        with ViewBag(), Body():
            yield from self.__to_account_input.compose()
            yield from self.__amount_input.compose()
            yield from self.__memo_input.compose()
        yield Static("Notice: transfer from savings will take 3 days", id="transfer-time-reminder")

    def _create_operation(
        self,
    ) -> TransferToSavingsOperation[Asset.Hive, Asset.Hbd] | TransferFromSavingsOperation[Asset.Hive, Asset.Hbd] | None:
        asset = self.__amount_input.value

        if not asset:
            return None
        if self.__to_button.value:
            return TransferToSavingsOperation(
                from_=self.app.world.profile_data.working_account.name,
                to=self.__to_account_input.value,
                amount=asset,
                memo=self.__memo_input.value,
            )
        elif self.__from_button.value:  # noqa: RET505
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
        pending_transfers = self.provider.content.pending_transfers
        max_number_of_request_ids: Final[int] = 100

        if not pending_transfers:
            return 0

        if len(pending_transfers) >= max_number_of_request_ids:
            raise RequestIdError("Maximum quantity of request ids is 100")

        sorted_transfers = sorted(pending_transfers, key=lambda x: x.request_id)
        last_occupied_id = sorted_transfers[-1].request_id
        return last_occupied_id + 1


class Savings(OperationBaseScreen):
    def create_left_panel(self) -> ComposeResult:
        with TabbedContent():
            yield SavingsInfo("savings info")
            yield SavingsTransfers("transfer")
