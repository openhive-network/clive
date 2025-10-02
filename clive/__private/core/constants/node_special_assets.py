from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

from clive.__private.core.constants.node import (
    HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION,
    VALUE_TO_REMOVE_SCHEDULED_TRANSFER,
    VESTS_TO_REMOVE_DELEGATION,
    VESTS_TO_REMOVE_POWER_DOWN,
)
from clive.__private.models.asset import Asset

SCHEDULED_TRANSFER_REMOVE_ASSETS: Final[tuple[Asset.Hive, Asset.Hbd]] = (
    Asset.hive(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
    Asset.hbd(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
)

DELEGATION_REMOVE_ASSETS: Final[tuple[Asset.Hive, Asset.Vests]] = (
    Asset.hive(VESTS_TO_REMOVE_DELEGATION),
    Asset.vests(VESTS_TO_REMOVE_DELEGATION),
)

POWER_DOWN_REMOVE_ASSET: Final[Asset.Vests] = Asset.vests(VESTS_TO_REMOVE_POWER_DOWN)

# claim account
HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION_ASSET: Final[Asset.Hive] = Asset.hive(
    HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION
)
