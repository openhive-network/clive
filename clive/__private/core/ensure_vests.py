from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.hive_vests_conversions import hive_to_vests
from clive.models import Asset

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive.models.aliased import DynamicGlobalProperties


def ensure_vests(value: Asset.VotingT, gdpo: DynamicGlobalProperties) -> Asset.Vests:
    """Convert vests/hive asset always to vests. To convert hive to vests gdpo must be provided."""
    if isinstance(value, Asset.Vests):
        return value

    return hive_to_vests(value, gdpo)


async def ensure_vests_async(value: Asset.VotingT, world: World) -> Asset.Vests:
    """Convert vests/hive asset always to vests. To convert hive to vests gdpo must be awaited."""
    if isinstance(value, Asset.Vests):
        return value

    gdpo = await world.app_state.get_dynamic_global_properties()
    return hive_to_vests(value, gdpo)
