from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Vertical

from clive.__private.core.formatters.humanize import (
    humanize_asset,
    humanize_datetime,
    humanize_hive_power,
    humanize_hp_vests_apr,
)
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.not_updated_yet import is_updated
from clive.__private.ui.widgets.apr import APR
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider


class WithdrawalInfo(Vertical, CliveWidget):
    """
    Widget that displays all withdrawal information.

    Attributes:
        DEFAULT_CSS: Default CSS for the withdrawal info widget.

    Args:
        provider: Data provider that provides the data for the widget.
    """

    DEFAULT_CSS = """
    WithdrawalInfo {
        height: auto;
    }

    Static {
        width: 1fr;
        text-align: center;
        text-style: bold;
    }

    #to-withdraw-header {
        margin-top: 1;
    }

    #withdrawal-info-date, #withdrawal-info-hp-amount {
        background: $panel-lighten-2;
    }

    #withdrawal-info-vests-amount {
        background: $panel-lighten-3;
    }
    """

    def __init__(self, provider: HivePowerDataProvider) -> None:
        super().__init__()
        self._provider = provider

    def compose(self) -> ComposeResult:
        yield SectionTitle("Next withdrawal")
        yield DynamicLabel(
            self._provider,
            "_content",
            self._get_next_withdrawal_date,
            id_="withdrawal-info-date",
            first_try_callback=is_updated,
        )
        yield SectionTitle("To withdraw", id_="to-withdraw-header")
        yield DynamicLabel(
            self._provider,
            "_content",
            self._get_to_withdraw_hp,
            id_="withdrawal-info-vests-amount",
            first_try_callback=is_updated,
        )
        yield DynamicLabel(
            self._provider,
            "_content",
            self._get_to_withdraw_vests,
            id_="withdrawal-info-hp-amount",
            first_try_callback=is_updated,
        )

    def _get_next_withdrawal_date(self, content: HivePowerData) -> str:
        return humanize_datetime(content.next_vesting_withdrawal)

    def _get_to_withdraw_hp(self, content: HivePowerData) -> str:
        return humanize_hive_power(content.to_withdraw.hp_balance)

    def _get_to_withdraw_vests(self, content: HivePowerData) -> str:
        return humanize_asset(content.to_withdraw.vests_balance)


class HivePowerAPR(APR):
    def _get_apr(self, content: HivePowerData) -> str:
        return humanize_hp_vests_apr(content.current_hp_apr, with_label=True)
