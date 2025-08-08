from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.core.constants.tui.texts import LOADING_TEXT
from clive.__private.core.formatters.humanize import humanize_asset
from clive.__private.ui.widgets.clive_basic import CliveDataTable, CliveDataTableRow

if TYPE_CHECKING:
    from typing import Final

    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData


class HpInfoTableRow(CliveDataTableRow):
    BALANCE_CELL_CLASS: Final[str] = "shares-balance-cell"

    def __init__(self, title: str) -> None:
        super().__init__(
            title,
            Static(LOADING_TEXT, classes=self.BALANCE_CELL_CLASS),
            Static(LOADING_TEXT, classes=self.BALANCE_CELL_CLASS),
            dynamic=True,
        )


class HpInfoTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Voting Power", id="shares-name-header")
        yield Static("Amount [HP]", classes="shares-balance-header")
        yield Static("Amount [VESTS]", classes="shares-balance-header")


class HpInfoTableOwnedRow(HpInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Owned")

    def get_new_values(self, content: HivePowerData) -> tuple[str, ...]:
        hp_balance = humanize_asset(content.owned_balance.hp_balance, show_symbol=False)
        vests_balance = humanize_asset(content.owned_balance.vests_balance, show_symbol=False)

        return hp_balance, vests_balance


class HpInfoTableReceivedRow(HpInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Received")

    def get_new_values(self, content: HivePowerData) -> tuple[str, ...]:
        hp_balance = humanize_asset(content.received_balance.hp_balance, show_symbol=False, sign_prefix="+")
        vests_balance = humanize_asset(content.received_balance.vests_balance, show_symbol=False, sign_prefix="+")

        return hp_balance, vests_balance


class HpInfoTableDelegatedRow(HpInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Delegated")

    def get_new_values(self, content: HivePowerData) -> tuple[str, ...]:
        hp_balance = humanize_asset(content.delegated_balance.hp_balance, show_symbol=False, sign_prefix="-")
        vests_balance = humanize_asset(content.delegated_balance.vests_balance, show_symbol=False, sign_prefix="-")

        return hp_balance, vests_balance


class HpInfoTablePowerDownRow(HpInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Power Down")

    def get_new_values(self, content: HivePowerData) -> tuple[str, ...]:
        hp_balance = humanize_asset(content.next_power_down.hp_balance, show_symbol=False, sign_prefix="-")
        vests_balance = humanize_asset(content.next_power_down.vests_balance, show_symbol=False, sign_prefix="-")

        return hp_balance, vests_balance


class HpInfoTableEffectiveRow(HpInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Effective")

    def get_new_values(self, content: HivePowerData) -> tuple[str, ...]:
        hp_balance = humanize_asset(content.total_balance.hp_balance, show_symbol=False)
        vests_balance = humanize_asset(content.total_balance.vests_balance, show_symbol=False)

        return hp_balance, vests_balance


class HpDataTable(CliveDataTable):
    def __init__(self) -> None:
        super().__init__(
            HpInfoTableHeader(),
            HpInfoTableOwnedRow(),
            HpInfoTableReceivedRow(),
            HpInfoTableDelegatedRow(),
            HpInfoTablePowerDownRow(),
            HpInfoTableEffectiveRow(),
            dynamic=True,
        )
