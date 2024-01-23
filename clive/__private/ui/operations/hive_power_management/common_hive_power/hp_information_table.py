from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_data_table import CliveDataTable, CliveDataTableRow, CliveTableRowWrapper
from clive.models import Asset

if TYPE_CHECKING:
    from textual.app import ComposeResult


class HpInformationTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static(classes="empty-header-column")
        yield Static("Amount in HP", classes="shares-balance-header")
        yield Static("Amount in VESTS", classes="shares-balance-header")
        yield Static("", classes="empty-column")
        yield Static("Additional info", classes="additional-info-header")


class HpInformationTableBaseRow(CliveDataTableRow):
    """Row of the clive data table with provider property."""

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.app.query_one(HivePowerDataProvider)


class HpInformationTableFirstRow(HpInformationTableBaseRow):
    def create_row(self) -> CliveTableRowWrapper | None:
        if self.provider.is_content_set:
            return CliveTableRowWrapper(
                [
                    "Owned",
                    f"{Asset.pretty_amount(self.provider.content.owned_balance.hp_balance)}",
                    f"{Asset.pretty_amount(self.provider.content.owned_balance.vests_balance)}",
                    "",
                    "Next withdrawal",
                ],
                cell_classes=[
                    "balance-row-title",
                    "shares-balance-column",
                    "shares-balance-column",
                    "empty-column",
                    "additional-header",
                ],
            )
        return None


class HpInformationTableSecondRow(HpInformationTableBaseRow):
    def create_row(self) -> CliveTableRowWrapper | None:
        if self.provider.is_content_set:
            return CliveTableRowWrapper(
                [
                    "Received",
                    f"+{Asset.pretty_amount(self.provider.content.received_balance.hp_balance)}",
                    f"+{Asset.pretty_amount(self.provider.content.received_balance.vests_balance)}",
                    "",
                    f"{humanize_datetime(self.provider.content.next_vesting_withdrawal)}",
                ],
                cell_classes=[
                    "balance-row-title",
                    "shares-balance-column",
                    "shares-balance-column",
                    "empty-column",
                    "additional-info-column",
                ],
            )
        return None


class HpInformationTableThirdRow(HpInformationTableBaseRow):
    def create_row(self) -> CliveTableRowWrapper | None:
        if self.provider.is_content_set:
            return CliveTableRowWrapper(
                [
                    "Delegated",
                    f"-{Asset.pretty_amount(self.provider.content.delegated_balance.hp_balance)}",
                    f"-{Asset.pretty_amount(self.provider.content.delegated_balance.vests_balance)}",
                    "",
                    "To withdraw",
                ],
                cell_classes=[
                    "balance-row-title",
                    "shares-balance-column",
                    "shares-balance-column",
                    "empty-column",
                    "additional-header",
                ],
            )
        return None


class HpInformationFourthRow(HpInformationTableBaseRow):
    def create_row(self) -> CliveTableRowWrapper | None:
        if self.provider.is_content_set:
            return CliveTableRowWrapper(
                [
                    "Power down",
                    f"-{Asset.pretty_amount(self.provider.content.next_power_down.hp_balance)}",
                    f"-{Asset.pretty_amount(self.provider.content.next_power_down.vests_balance)}",
                    "",
                    f"{Asset.pretty_amount(self.provider.content.to_withdraw.hp_balance)} HP",
                ],
                cell_classes=[
                    "balance-row-title",
                    "shares-balance-column",
                    "shares-balance-column",
                    "empty-column",
                    "additional-info-column",
                ],
            )
        return None


class HpInformationFifthRow(HpInformationTableBaseRow):
    def create_row(self) -> CliveTableRowWrapper | None:
        if self.provider.is_content_set:
            return CliveTableRowWrapper(
                [
                    "Total",
                    f"{Asset.pretty_amount(self.provider.content.total_balance.hp_balance)}",
                    f"{Asset.pretty_amount(self.provider.content.total_balance.vests_balance)}",
                    "",
                    f"{Asset.pretty_amount(self.provider.content.to_withdraw.vests_balance)} VESTS",
                ],
                cell_classes=[
                    "balance-row-title",
                    "shares-balance-column",
                    "shares-balance-column",
                    "empty-column",
                    "additional-info-column",
                ],
            )
        return None


class HpInformationSixthRow(HpInformationTableBaseRow):
    def create_row(self) -> CliveTableRowWrapper | None:
        if self.provider.is_content_set:
            return CliveTableRowWrapper(
                ["", f"APR interest for HP/VESTS ≈ {self.provider.content.current_hp_apr} %"],
                cell_classes=["empty-column-fifth-row", "row-with-apr"],
            )
        return None


class HpInformationTable(CliveDataTable):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        self._table_rows = [
            HpInformationTableFirstRow("with-date", dynamic=True),
            HpInformationTableSecondRow("with-to-withdraw-hp", dynamic=True),
            HpInformationTableThirdRow("with-to-withdraw-vests", dynamic=True),
            HpInformationFourthRow("with-routes", dynamic=True),
            HpInformationFifthRow("test", dynamic=True),
            HpInformationSixthRow("with-apr", dynamic=True),
        ]
        super().__init__(table_rows=self._table_rows)

    def create_table_headlines(self) -> ComposeResult:
        yield HpInformationTableHeader()
