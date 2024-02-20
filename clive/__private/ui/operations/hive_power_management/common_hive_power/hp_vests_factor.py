from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.hive_vests_conversions import hive_to_vests
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.models import Asset

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider


class HpVestsFactor(DynamicLabel):
    DEFAULT_CSS = """
    HpVestsFactor {
        width: 1fr;
        height: 1;
        margin-bottom: 1;
        align: center middle;
        background: $warning;
        color: $text;
    }
    """

    def __init__(self, provider: HivePowerDataProvider):
        super().__init__(
            obj_to_watch=provider, attribute_name="_content", callback=self._get_hp_vests_factor, init=False
        )

    def _get_hp_vests_factor(self, content: HivePowerData) -> str:
        factor = hive_to_vests(1000, content.gdpo)
        return f"HP is calculated to VESTS with the factor: 1.000 HP -> {Asset.pretty_amount(factor)} VESTS"
