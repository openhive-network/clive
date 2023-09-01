from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Final

from textual import on, work
from textual.containers import Container, Grid, Horizontal, ScrollableContainer
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, RadioButton, RadioSet, Static, TabbedContent

from clive.__private.config import settings
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
from clive.models import Asset
from schemas.__private.operations.transfer_from_savings_operation import TransferFromSavingsOperation
from schemas.__private.operations.transfer_to_savings_operation import TransferToSavingsOperation
from schemas.database_api.fundaments_of_reponses import SavingsWithdrawalsFundament

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


SavingsWithdrawalsT = SavingsWithdrawalsFundament[Asset.Hive, Asset.Hbd]


@dataclass
class SavingsData:
    pending_transfers: list[SavingsWithdrawalsT] | None = None
    hbd_interest_rate: int = 1000
    last_interest_payment: datetime = field(default_factory=lambda: datetime.utcfromtimestamp(0))


class SavingsDataProvider(CliveWidget):
    """
    A class for retrieving information about savings stored in a SavingsData dataclass.

    To access the data after initializing the class, use the content property.
    """

    content: SavingsData = var(SavingsData())  # type: ignore[assignment]
    """It is used to check whether savings data has been refreshed and to store savings data."""

    def __init__(self) -> None:
        super().__init__()
        self.set_interval(settings.get("node.refresh_rate", 1.5), self._update_savings_data)  # type: ignore[arg-type]

    @work(name="savings data update worker")
    async def _update_savings_data(self) -> None:
        working_account_name = self.app.world.profile_data.working_account.name

        gdpo = await self.app.world.app_state.get_dynamic_global_properties()
        response_db_api = await self.app.world.node.api.database_api.find_accounts(accounts=[working_account_name])
        pending_transfers = await self.app.world.node.api.database_api.find_savings_withdrawals(
            account=working_account_name
        )

        new_savings_data = SavingsData(
            hbd_interest_rate=gdpo.hbd_interest_rate,
            last_interest_payment=response_db_api.accounts[0].savings_hbd_last_interest_payment,
            pending_transfers=pending_transfers.withdrawals,
        )

        if self.content != new_savings_data:
            self.content = new_savings_data


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
    def __init__(self, provider: SavingsDataProvider) -> None:
        super().__init__(account=self.app.world.profile_data.working_account)
        self.__provider = provider

    def compose(self) -> ComposeResult:
        def get_interest_date() -> str:
            last_interest_payment = self.__provider.content.last_interest_payment.replace(tzinfo=None).isoformat()

            if last_interest_payment == "1970-01-01T00:00:00":
                return "Last interest payment: Never"
            return f"""Last interest payment: {last_interest_payment} (UTC)"""

        def get_estimated_interest() -> str:
            return f"Interest since last payment: {self._account.data.hbd_unclaimed.amount} HBD"

        def get_interest_rate_for_hbd() -> str:
            return f"APR interest rate for HBD($) is {self.__provider.content.hbd_interest_rate / 100}%"

        with Horizontal():
            yield SavingsBalances(self._account)
            with Container(id="interest-rate"):
                yield self.create_dynamic_label(get_interest_date, "interest-rate-date")
                yield self.create_dynamic_label(get_estimated_interest, "interest-rate-value")
                yield self.create_dynamic_label(get_interest_rate_for_hbd, "interest-rate-value-percent")


class PendingTransfer(CliveWidget):
    """class which represents one pending transfer."""

    def __init__(self, transfer: SavingsWithdrawalsT):
        super().__init__()
        self.__transfer = transfer

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static(self.__transfer.to, classes=odd)
            yield Static(Asset.to_legacy(self.__transfer.amount), classes=even)
            yield Static(str(self.__realized_on), classes=odd)
            yield Static(self.__transfer.memo, classes=even)
            yield CliveButton("Cancel", id_="delete-transfer-button")

    @property
    def __realized_on(self) -> str:
        return self.__transfer.complete.replace(tzinfo=None).isoformat()

    @on(Button.Pressed, "#delete-transfer-button")
    def move_to_cancel_transfer(self) -> None:
        self.app.push_screen(CancelTransferFromSavings(self.__transfer))


class PendingHeader(CliveWidget):
    def compose(self) -> ComposeResult:
        with Horizontal(id="header-pending"):
            yield Static("To", classes=even)
            yield Static("Amount", classes=odd)
            yield Static("Realized on (UTC)", classes=even)
            yield Static("Memo", classes=odd)
            yield Static()


class PendingTransfers(ScrollableContainer, CliveWidget):
    def __init__(self, pending_transfers: list[SavingsWithdrawalsT] | None = None) -> None:
        super().__init__()
        self.__pending_transfers = pending_transfers

    def compose(self) -> ComposeResult:
        if self.__pending_transfers:
            number_of_transfers = len(self.__pending_transfers)
            yield Static(f"Number of transfers from savings now: {number_of_transfers}", classes="number-of-transfers")
            yield PendingHeader()
            for transfer in self.__pending_transfers:
                yield PendingTransfer(transfer)
        else:
            yield Static("No transfers from savings now", classes="number-of-transfers")


class SavingsInfo(ScrollableTabPane, CliveWidget):
    def __init__(self, provider: SavingsDataProvider, title: TextType) -> None:
        super().__init__(title=title)
        self.__provider = provider

    def compose(self) -> ComposeResult:
        yield SavingsInterestInfo(self.__provider)
        yield PendingTransfers()

    def on_mount(self) -> None:
        self.watch(self.__provider, "content", callback=self.__sync_pending_transfers)

    def __sync_pending_transfers(self, content: SavingsData) -> None:
        try:
            pending_transfers_container = self.query_one(PendingTransfers)
        except NoMatches:
            return

        pending_transfers_container.remove()
        new_transfers_item = PendingTransfers(content.pending_transfers)
        self.mount(new_transfers_item)


class SavingsTransfers(ScrollableTabPane, OperationMethods):
    def __init__(self, provider: SavingsDataProvider, title: TextType = "") -> None:
        super().__init__(title=title)
        self.__provider = provider

        self.__amount_input = AssetAmountInput()
        self.__memo_input = MemoInput()
        self.__to_account_input = AccountNameInput(value=self.app.world.profile_data.working_account.name)

        self.__to_button = CliveRadioButton("transfer to savings", id="to-savings-choose", value=True)
        self.__from_button = CliveRadioButton("transfer from savings", id="from-savings-choose")

    def compose(self) -> ComposeResult:
        yield Static("Choose type of operation", id="savings-transfer-header")
        with RadioSet(id="operation-type-choose"):
            yield self.__to_button
            yield self.__from_button

        yield SavingsBalances(self.app.world.profile_data.working_account, classes="transfer-savings-balances")
        with Body():
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
        try:
            request_id = self.__create_request_id()
        except RequestIdError:
            self.notify("Maximum quantity of request ids is 100!", severity="error")
            return None

        return TransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            to=self.__to_account_input.value,
            amount=asset,
            memo=self.__memo_input.value,
            request_id=request_id,
        )

    def __create_request_id(self) -> int:
        pending_transfers = self.__provider.content.pending_transfers
        max_number_of_request_ids: Final[int] = 100

        if not pending_transfers:
            return 0

        if len(pending_transfers) >= max_number_of_request_ids:
            raise RequestIdError("Maximum quantity of request ids is 100")

        sorted_transfers = sorted(pending_transfers, key=lambda x: x.request_id)
        last_occupied_id = sorted_transfers[-1].request_id

        return int(last_occupied_id) + 1


class Savings(OperationBaseScreen):
    def __init__(self) -> None:
        self.__provider = SavingsDataProvider()
        super().__init__()

    def create_left_panel(self) -> ComposeResult:
        with TabbedContent():
            yield SavingsInfo(self.__provider, "savings info")
            yield SavingsTransfers(self.__provider, "transfer")
