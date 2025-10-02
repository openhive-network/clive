from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.models.asset import Asset

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive.__private.models.schemas import DynamicGlobalProperties


def ensure_vests(value: Asset.VotingT, gdpo: DynamicGlobalProperties) -> Asset.Vests:
    """
    Convert vests/hive asset always to vests. To convert hive to vests gdpo must be provided.

    Args:
        value: The asset to convert, can be either vests or hive.
        gdpo: The dynamic global properties to use for conversion if needed.

    Returns:
        The converted asset to vests.
    """
    if isinstance(value, Asset.Vests):
        return value

    return iwax.calculate_hp_to_vests(value, gdpo)


async def ensure_vests_async(value: Asset.VotingT, world: World) -> Asset.Vests:
    """
    Convert vests/hive asset always to vests. To convert hive to vests gdpo must be awaited.

    Args:
        value: The asset to convert, can be either vests or hive.
        world: The world instance to access the dynamic global properties.

    Returns:
        The converted asset to vests.
    """
    if isinstance(value, Asset.Vests):
        return value

    gdpo = await world.node.cached.dynamic_global_properties
    return iwax.calculate_hp_to_vests(value, gdpo)
