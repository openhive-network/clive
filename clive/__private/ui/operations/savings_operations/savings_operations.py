from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Container, Grid, Horizontal
from textual.widgets import Button, Label, LoadingIndicator, RadioSet, Static, TabPane

from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.data_providers.savings_data_provider import SavingsDataProvider
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.bindings import CartBinding, OperationActionBindings
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.operations.operation_summary.cancel_transfer_from_savings import (
    CancelTransferFromSavings,
)
from clive.__private.ui.widgets.account_referencing_widget import AccountReferencingWidget
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_radio_button import CliveRadioButton
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.notice import Notice
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle
from clive.exceptions import RequestIdError
from clive.models import Asset
from schemas.operations import (
    TransferFromSavingsOperation,
    TransferToSavingsOperation,
)

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
    from clive.models.aliased import SavingsWithdrawals


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

        self.interest_data_container = Container(id="interest-data-container")

    @property
    def provider(self) -> SavingsDataProvider:
        return self.screen.query_one(SavingsDataProvider)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield SavingsBalances(self._account)
            with self.interest_data_container:
                yield LoadingIndicator()

    def on_mount(self) -> None:
        self.watch(self.provider, "_content", callback=self.sync_data)

    def sync_data(self, content: SavingsData | None) -> None:
        if content is None:  # data not received yet
            return

        def get_interest_date() -> str:
            last_interest_payment = humanize_datetime(content.last_interest_payment)
            return f"""Last interest payment: {last_interest_payment} (UTC)"""

        def get_estimated_interest() -> str:
            return f"Interest since last payment: {self._account.data.hbd_unclaimed.amount} HBD"

        def get_interest_rate_for_hbd() -> str:
            return f"APR interest rate for HBD($) is {content.hbd_interest_rate / 100}%"

        with self.app.batch_update():
            self.interest_data_container.query("*").remove()
            self.interest_data_container.mount_all(
                [
                    self.create_dynamic_label(get_interest_date, "interest-info-row-odd"),
                    self.create_dynamic_label(get_estimated_interest, "interest-info-row-even"),
                    self.create_dynamic_label(get_interest_rate_for_hbd, "interest-info-row-odd"),
                ]
            )


class PendingTransfersHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("To", classes=ODD_CLASS_NAME)
        yield Label("Amount", classes=EVEN_CLASS_NAME)
        yield Label("Realized on (UTC)", classes=ODD_CLASS_NAME)
        yield Label("Memo", classes=EVEN_CLASS_NAME)
        yield Label()


class PendingTransfer(CliveCheckerboardTableRow):
    def __init__(self, pending_transfer: SavingsWithdrawals):
        super().__init__(
            CliveCheckerBoardTableCell(pending_transfer.to),
            CliveCheckerBoardTableCell(Asset.to_legacy(pending_transfer.amount)),
            CliveCheckerBoardTableCell(humanize_datetime(pending_transfer.complete)),
            CliveCheckerBoardTableCell(pending_transfer.memo),
            CliveCheckerBoardTableCell(CliveButton("Cancel", variant="error", id_="delete-transfer-button")),
        )
        self._pending_transfer = pending_transfer

    @on(Button.Pressed, "#delete-transfer-button")
    def push_operation_summary_screen(self) -> None:
        self.app.push_screen(CancelTransferFromSavings(self._pending_transfer))


class PendingTransfers(CliveCheckerboardTable):
    def __init__(self) -> None:
        super().__init__(
            Static("", id="pending-transfers-table-title"),
            PendingTransfersHeader(),
            dynamic=True,
        )
        self._previous_pending_transfers: list[SavingsWithdrawals] | None = None

    def create_dynamic_rows(self, content: SavingsData) -> list[PendingTransfer]:
        self._previous_pending_transfers = content.pending_transfers

        self._title: Static
        self._title.update(f"Current pending transfers (amount: {len(content.pending_transfers)})")
        return [PendingTransfer(pending_transfer) for pending_transfer in content.pending_transfers]

    def get_no_content_available_widget(self) -> Static:
        return Static("You have no pending transfers", id="no-pending-transfers-info")

    @property
    def is_anything_to_display(self) -> bool:
        return len(self.provider.content.pending_transfers) != 0

    @property
    def check_if_should_be_updated(self) -> bool:
        return self._previous_pending_transfers != self.provider.content.pending_transfers

    @property
    def provider(self) -> SavingsDataProvider:
        return self.screen.query_one(SavingsDataProvider)


class SavingsInfo(TabPane, CliveWidget):
    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield SavingsInterestInfo()
            yield PendingTransfers()


class SavingsTransfers(TabPane, OperationActionBindings):
    def __init__(self, title: TextType) -> None:
        super().__init__(title=title)

        self._amount_input = LiquidAssetAmountInput()
        self._memo_input = MemoInput()
        self._to_account_input = AccountNameInput("To", value=self.default_receiver)

        self._to_button = CliveRadioButton("transfer to savings", id="to-savings-choose", value=True)
        self._from_button = CliveRadioButton("transfer from savings", id="from-savings-choose")

        self._transfer_time_reminder = Notice("transfer from savings will take 3 days")
        self._transfer_time_reminder.visible = False

    @property
    def default_receiver(self) -> str:
        return self.app.world.profile_data.working_account.name

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield Static("Choose type of operation", id="savings-transfer-type-header")
            with RadioSet(id="operation-type-choose"):
                yield self._to_button
                yield self._from_button
            yield SavingsBalances(self.app.world.profile_data.working_account)
            yield self._transfer_time_reminder
            yield SectionTitle("Perform a transfer to savings")
            with Body():
                yield self._to_account_input
                yield self._amount_input
                yield self._memo_input

    @on(RadioSet.Changed)
    def transfer_type_changed(self, event: RadioSet.Changed) -> None:
        section_title = self.query_one(SectionTitle)
        if event.radio_set.pressed_button.id == "from-savings-choose":  # type: ignore[union-attr]
            self._transfer_time_reminder.visible = True
            section_title.update("Perform a transfer from savings")
            return
        self._transfer_time_reminder.visible = False
        section_title.update("Perform a transfer to savings")

    def _create_operation(
        self,
    ) -> TransferToSavingsOperation | TransferFromSavingsOperation | None:
        # So all inputs are validated together, and not one by one.
        if not CliveValidatedInput.validate_many(self._to_account_input, self._amount_input, self._memo_input):
            return None

        data = {
            "from_": self.default_receiver,
            "to": self._to_account_input.value_or_error,
            "amount": self._amount_input.value_or_error,
            "memo": self._memo_input.value_or_error,
        }

        if self._to_button.value:
            return TransferToSavingsOperation(**data)

        try:
            request_id = self._create_request_id()
        except RequestIdError as error:
            self.notify(str(error), severity="error")
            return None

        return TransferFromSavingsOperation(**data, request_id=request_id)

    def _create_request_id(self) -> int:
        provider = self.screen.query_one(SavingsDataProvider)
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
