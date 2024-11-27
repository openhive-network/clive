from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.containers import Horizontal

from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.operation_base_screen import OperationBaseScreen
from clive.__private.ui.screens.operations.hive_power_management.common_hive_power.additional_info_widgets import (
    HivePowerAPR,
    WithdrawalInfo,
)
from clive.__private.ui.screens.operations.hive_power_management.common_hive_power.hp_information_table import (
    HpDataTable,
)
from clive.__private.ui.screens.operations.hive_power_management.common_hive_power.hp_vests_factor import HpVestsFactor
from clive.__private.ui.screens.operations.hive_power_management.delegate_hive_power.delegate_hive_power import (
    DelegateHivePower,
)
from clive.__private.ui.screens.operations.hive_power_management.power_down.power_down import PowerDown
from clive.__private.ui.screens.operations.hive_power_management.power_up.power_up import PowerUp
from clive.__private.ui.screens.operations.hive_power_management.withdraw_routes.withdraw_routes import WithdrawRoutes
from clive.__private.ui.widgets.clive_basic import CliveTabbedContent
from clive.__private.ui.widgets.location_indicator import LocationIndicator

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
            yield LocationIndicator("hive power management")
            yield HpVestsFactor(provider)
            with Horizontal(id="hive-power-info"):
                yield HpDataTable()
                yield WithdrawalInfo(provider)
            yield HivePowerAPR(provider)
            with CliveTabbedContent():
                yield PowerUp(POWER_UP_TAB_LABEL)
                yield PowerDown(POWER_DOWN_TAB_LABEL)
                yield WithdrawRoutes(WITHDRAW_ROUTES_TAB_LABEL)
                yield DelegateHivePower(DELEGATE_HIVE_POWER_LABEL)
