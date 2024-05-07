from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Vertical
from textual.widgets import Static

from clive.__private.core.formatters.humanize import humanize_asset, humanize_datetime, humanize_hive_power
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider


class WithdrawalInfo(Vertical, CliveWidget):
    """Widget that displays all withdrawal information."""

    DEFAULT_CSS = """
    WithdrawalInfo {
        height: auto;
    }

    Static {
        width: 1fr;
        text-align: center;
        text-style: bold;
    }

    .withdrawal-info-header {
        background: $primary-background;
    }

    #to-withdraw-header {
        margin-top: 1;
    }

    #withdrawal-info-date, #withdrawal-info-vests-amount {
        background: $accent;
    }

    #withdrawal-info-hp-amount {
        background: $accent-lighten-1;
    }
    """

    def __init__(self, provider: HivePowerDataProvider):
        super().__init__()
        self._provider = provider

    def compose(self) -> ComposeResult:
        yield Static("Next withdrawal", classes="withdrawal-info-header")
        yield DynamicLabel(
            self._provider, "_content", self._get_next_withdrawal_date, id_="withdrawal-info-date", init=False
        )
        yield Static("To withdraw", classes="withdrawal-info-header", id="to-withdraw-header")
        yield DynamicLabel(
            self._provider, "_content", self._get_to_withdraw_hp, id_="withdrawal-info-vests-amount", init=False
        )
        yield DynamicLabel(
            self._provider, "_content", self._get_to_withdraw_vests, id_="withdrawal-info-hp-amount", init=False
        )

    def _get_next_withdrawal_date(self, content: HivePowerData) -> str:
        return humanize_datetime(content.next_vesting_withdrawal)

    def _get_to_withdraw_hp(self, content: HivePowerData) -> str:
        return humanize_hive_power(content.to_withdraw.hp_balance)

    def _get_to_withdraw_vests(self, content: HivePowerData) -> str:
        return humanize_asset(content.to_withdraw.vests_balance)


class APR(DynamicLabel):
    DEFAULT_CSS = """
    APR {
        height: 1;
        margin-top: 1;
        background: $primary-background;
        text-style: bold;
        align: center middle;
        width: 1fr;
    }
    """

    def __init__(self, provider: HivePowerDataProvider):
        super().__init__(obj_to_watch=provider, attribute_name="_content", callback=self._get_apr, init=False)
        self._provider = provider

    def _get_apr(self, content: HivePowerData) -> str:
        return f"APR interest for HP/VESTS ≈ {content.current_hp_apr} %"
