from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.models import Asset

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive.__private.models.schemas import DynamicGlobalProperties


def ensure_vests(value: Asset.VotingT, gdpo: DynamicGlobalProperties) -> Asset.Vests:
    """Convert vests/hive asset always to vests. To convert hive to vests gdpo must be provided."""
    if isinstance(value, Asset.Vests):
        return value

    return iwax.calculate_hp_to_vests(value, gdpo)


async def ensure_vests_async(value: Asset.VotingT, world: World) -> Asset.Vests:
    """Convert vests/hive asset always to vests. To convert hive to vests gdpo must be awaited."""
    if isinstance(value, Asset.Vests):
        return value

    gdpo = await world.node.cached.dynamic_global_properties
    return iwax.calculate_hp_to_vests(value, gdpo)
