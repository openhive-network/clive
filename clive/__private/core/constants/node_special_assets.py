from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

from clive.__private.core.constants.node import (
    VALUE_TO_REMOVE_SCHEDULED_TRANSFER,
    VESTS_TO_REMOVE_DELEGATION,
)
from clive.__private.models import Asset

# removal values represented as assets
SCHEDULED_TRANSFER_REMOVE_ASSETS: Final[tuple[Asset.Hive, Asset.Hbd]] = (
    Asset.hive(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
    Asset.hbd(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
)

DELEGATIONS_REMOVE_ASSETS: Final[tuple[Asset.Hive, Asset.Vests]] = (
    Asset.hive(VESTS_TO_REMOVE_DELEGATION),
    Asset.vests(VESTS_TO_REMOVE_DELEGATION),
)
