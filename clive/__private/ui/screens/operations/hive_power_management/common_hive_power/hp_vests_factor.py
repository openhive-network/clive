from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.formatters.humanize import humanize_vest_to_hive_ratio
from clive.__private.ui.not_updated_yet import is_updated
from clive.__private.ui.widgets.notice import Notice

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider


class HpVestsFactor(Notice):
    def __init__(self, provider: HivePowerDataProvider) -> None:
        super().__init__(
            obj_to_watch=provider,
            attribute_name="_content",
            callback=self._get_hp_vests_factor,
            first_try_callback=is_updated,
        )

    def _get_hp_vests_factor(self, content: HivePowerData) -> str:
        factor = humanize_vest_to_hive_ratio(content.gdpo, show_symbol=True)
        return f"HP is calculated to VESTS with the factor: 1.000 HP -> {factor}"
