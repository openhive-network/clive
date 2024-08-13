from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Grid, Horizontal
from textual.widgets import Button, Label, RadioSet, Static, TabPane

from clive.__private.core.formatters.humanize import humanize_datetime, humanize_hbd_savings_apr
from clive.__private.core.percent_conversions import hive_percent_to_percent
from clive.__private.ui.data_providers.savings_data_provider import SavingsDataProvider
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.operations.bindings import CartBinding, OperationActionBindings
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.operations.operation_summary.cancel_transfer_from_savings import (
    CancelTransferFromSavings,
)
from clive.__private.ui.widgets.apr import APR
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_data_table import CliveDataTable, CliveDataTableRow
from clive.__private.ui.widgets.clive_radio_button import CliveRadioButton
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive.__private.ui.widgets.location_indicator import LocationIndicator
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.notice import Notice
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import Section
from clive.__private.ui.widgets.section_title import SectionTitle
from clive.__private.ui.widgets.tracked_account_referencing_widget import TrackedAccountReferencingWidget
from clive.exceptions import RequestIdError
from clive.models import Asset
from schemas.operations import (
    TransferFromSavingsOperation,
    TransferToSavingsOperation,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
    from clive.models.aliased import SavingsWithdrawals


class Body(Grid):
    """Holds all places using to create transfers from/to savings."""


class SavingsBalancesHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static()
        yield Static("Savings balance", id="savings-title")


class SavingsHiveRow(CliveDataTableRow):
    def __init__(self) -> None:
        super().__init__("HIVE", Static("loading..."), dynamic=True)

    def get_new_values(self, content: SavingsData) -> tuple[str]:
        return (Asset.pretty_amount(content.hive_savings_balance),)


class SavingsHbdRow(CliveDataTableRow):
    def __init__(self) -> None:
        super().__init__("HBD", Static("loading..."), dynamic=True)

    def get_new_values(self, content: SavingsData) -> tuple[str]:
        return (Asset.pretty_amount(content.hbd_savings_balance),)


class SavingsBalancesTable(CliveDataTable):
    def __init__(self) -> None:
        super().__init__(
            SavingsBalancesHeader(),
            SavingsHbdRow(),
            SavingsHiveRow(),
            dynamic=True,
        )


class SavingsInterestInfo(TrackedAccountReferencingWidget):
    def __init__(self) -> None:
        super().__init__(account=self.profile_data.accounts.working)

    @property
    def provider(self) -> SavingsDataProvider:
        return self.screen.query_one(SavingsDataProvider)

    def compose(self) -> ComposeResult:
        yield SectionTitle("Interest data", variant="dark")
        yield DynamicLabel(
            self.provider,
            "_content",
            callback=self._get_unclaimed_hbd,
            classes="interest-info-row-even",
            first_try_callback=lambda content: content is not None,
        )
        yield DynamicLabel(
            self.provider,
            "_content",
            callback=self._get_last_payment_date,
            classes="interest-info-row-odd",
            first_try_callback=lambda content: content is not None,
        )

    def _get_last_payment_date(self, content: SavingsData) -> str:
        last_interest_payment = humanize_datetime(content.last_interest_payment)
        return f"""Last payment: {last_interest_payment} (UTC)"""

    def _get_unclaimed_hbd(self, content: SavingsData) -> str:
        return f"Interest since last payment: {Asset.pretty_amount(content.hbd_unclaimed)} HBD"


class PendingTransfersHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("To", classes=ODD_CLASS_NAME)
        yield Label("Amount", classes=EVEN_CLASS_NAME)
        yield Label("Realized on (UTC)", classes=ODD_CLASS_NAME)
        yield Label("Memo", classes=EVEN_CLASS_NAME)
        yield Label()


class PendingTransfer(CliveCheckerboardTableRow):
    def __init__(self, pending_transfer: SavingsWithdrawals, aligned_amount: str) -> None:
        super().__init__(
            CliveCheckerBoardTableCell(pending_transfer.to),
            CliveCheckerBoardTableCell(aligned_amount),
            CliveCheckerBoardTableCell(humanize_datetime(pending_transfer.complete)),
            CliveCheckerBoardTableCell(pending_transfer.memo),
            CliveCheckerBoardTableCell(CliveButton("Cancel", variant="error", id_="delete-transfer-button")),
        )
        self._pending_transfer = pending_transfer

    @on(Button.Pressed, "#delete-transfer-button")
    def push_operation_summary_screen(self) -> None:
        self.app.push_screen(CancelTransferFromSavings(self._pending_transfer))


class PendingTransfers(CliveCheckerboardTable):
    ATTRIBUTE_TO_WATCH = "_content"

    def __init__(self) -> None:
        super().__init__(header=PendingTransfersHeader(), title=SectionTitle(""))
        self._previous_pending_transfers: list[SavingsWithdrawals] | NotUpdatedYet = NotUpdatedYet()

    def create_dynamic_rows(self, content: SavingsData) -> list[PendingTransfer]:
        self._title: Static
        self._title.update(f"Current pending transfers (amount: {len(content.pending_transfers)})")

        aligned_amounts = content.get_pending_transfers_aligned_amounts()

        return [
            PendingTransfer(pending_transfer, aligned_amount)
            for pending_transfer, aligned_amount in zip(content.pending_transfers, aligned_amounts, strict=True)
        ]

    def get_no_content_available_widget(self) -> Static:
        return NoContentAvailable("You have no pending transfers")

    def is_anything_to_display(self, content: SavingsData) -> bool:
        return len(content.pending_transfers) != 0

    def check_if_should_be_updated(self, content: SavingsData) -> bool:
        return self._previous_pending_transfers != content.pending_transfers

    @property
    def object_to_watch(self) -> SavingsDataProvider:
        return self.screen.query_one(SavingsDataProvider)

    def update_previous_state(self, content: SavingsData) -> None:
        self._previous_pending_transfers = content.pending_transfers


class PendingTransfersPane(TabPane, CliveWidget):
    TITLE: Final[str] = "pending transfers"

    def __init__(self) -> None:
        super().__init__(title=self.TITLE)

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield PendingTransfers()


class SavingsTransfers(TabPane, OperationActionBindings):
    TITLE: Final[str] = "transfer"

    def __init__(self) -> None:
        super().__init__(title=self.TITLE)

        self._amount_input = LiquidAssetAmountInput()
        self._memo_input = MemoInput()
        self._to_account_input = AccountNameInput("To", value=self.default_receiver)

        self._to_button = CliveRadioButton("transfer to savings", id="to-savings-choose", value=True)
        self._from_button = CliveRadioButton("transfer from savings", id="from-savings-choose")

        self._transfer_time_reminder = Notice("transfer from savings will take 3 days")
        self._transfer_time_reminder.visible = False

    @property
    def default_receiver(self) -> str:
        return self.profile_data.accounts.working.name

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield Static("Choose type of operation", id="savings-transfer-type-header")
            with RadioSet(id="operation-type-choose"):
                yield self._to_button
                yield self._from_button
            yield self._transfer_time_reminder
            with Section("Perform a transfer to savings"), Body():
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
            operation for operation in self.profile_data.cart if isinstance(operation, TransferFromSavingsOperation)
        ]
        return savings_data.create_request_id(future_transfers=transfer_from_savings_operations_in_cart)


class SavingsAPR(APR):
    def _get_apr(self, content: SavingsData) -> str:
        return humanize_hbd_savings_apr(hive_percent_to_percent(content.hbd_interest_rate), with_label=True)


class Savings(OperationBaseScreen, CartBinding):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def create_left_panel(self) -> ComposeResult:
        yield LocationIndicator("Savings operations")
        with SavingsDataProvider() as provider:
            with Horizontal(id="savings-info-container"):
                yield SavingsBalancesTable()
                yield SavingsInterestInfo()
            yield SavingsAPR(provider)
            with CliveTabbedContent():
                yield PendingTransfersPane()
                yield SavingsTransfers()
