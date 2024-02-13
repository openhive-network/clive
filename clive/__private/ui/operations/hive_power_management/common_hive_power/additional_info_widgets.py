from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Vertical
from textual.widgets import Static

from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.models import Asset

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
        yield DynamicLabel(self._provider, "_content", self._get_next_withdrawal_date, id_="withdrawal-info-date")
        yield Static("To withdraw", classes="withdrawal-info-header", id="to-withdraw-header")
        yield DynamicLabel(self._provider, "_content", self._get_to_withdraw_hp, id_="withdrawal-info-vests-amount")
        yield DynamicLabel(self._provider, "_content", self._get_to_withdraw_vests, id_="withdrawal-info-hp-amount")

    def _get_next_withdrawal_date(self, content: HivePowerData) -> str:
        if self._provider.is_content_set:
            return humanize_datetime(content.next_vesting_withdrawal)
        return "loading..."

    def _get_to_withdraw_hp(self, content: HivePowerData) -> str:
        if self._provider.is_content_set:
            return f"{Asset.pretty_amount(content.to_withdraw.hp_balance)} HP"
        return "loading..."

    def _get_to_withdraw_vests(self, content: HivePowerData) -> str:
        if self._provider.is_content_set:
            return f"{Asset.pretty_amount(content.to_withdraw.vests_balance)} VESTS"
        return "loading..."


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
        super().__init__(obj_to_watch=provider, attribute_name="_content", callback=self._get_apr)
        self._provider = provider

    def _get_apr(self, content: HivePowerData) -> str:
        if self._provider.is_content_set:
            return f"APR interest for HP/VESTS ≈ {content.current_hp_apr} %"
        return "loading..."
