from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.containers import Horizontal

from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.hive_power_management.common_hive_power.additional_info_widgets import (
    APR,
    WithdrawalInfo,
)
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_information_table import (
    HpInfoTableDelegatedRow,
    HpInfoTableEffectiveRow,
    HpInfoTableHeader,
    HpInfoTableOwnedRow,
    HpInfoTablePowerDownRow,
    HpInfoTableReceivedRow,
)
from clive.__private.ui.operations.hive_power_management.delegate_hive_power.delegate_hive_power import (
    DelegateHivePower,
)
from clive.__private.ui.operations.hive_power_management.power_down.power_down import PowerDown
from clive.__private.ui.operations.hive_power_management.power_up.power_up import PowerUp
from clive.__private.ui.operations.hive_power_management.withdraw_routes.withdraw_routes import WithdrawRoutes
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_data_table import CliveDataTable
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent

if TYPE_CHECKING:
    from textual.app import ComposeResult

POWER_UP_TAB_LABEL: Final[str] = "Power up"
POWER_DOWN_TAB_LABEL: Final[str] = "Power down"
WITHDRAW_ROUTES_TAB_LABEL: Final[str] = "Withdraw routes"
DELEGATE_HIVE_POWER_LABEL: Final[str] = "Delegate"


class HivePowerManagement(OperationBaseScreen):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def create_left_panel(self) -> ComposeResult:
        with HivePowerDataProvider() as provider:
            yield BigTitle("hive power management")
            with Horizontal(id="hive-power-info"):
                yield CliveDataTable(
                    HpInfoTableHeader(),
                    HpInfoTableOwnedRow(),
                    HpInfoTableReceivedRow(),
                    HpInfoTableDelegatedRow(),
                    HpInfoTablePowerDownRow(),
                    HpInfoTableEffectiveRow(),
                )
                yield WithdrawalInfo(provider)
            yield APR(provider)
            with CliveTabbedContent():
                yield PowerUp(POWER_UP_TAB_LABEL)
                yield PowerDown(POWER_DOWN_TAB_LABEL)
                yield WithdrawRoutes(WITHDRAW_ROUTES_TAB_LABEL)
                yield DelegateHivePower(DELEGATE_HIVE_POWER_LABEL)
