from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.core.constants import HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION
from clive.models import Asset
from schemas.operations import ClaimAccountOperation


@dataclass(kw_only=True)
class ProcessWitnessUpdate(OperationCommand):
    owner: str
    """None means RC will be used instead of payment in Hive"""

    async def _create_operation(self) -> ClaimAccountOperation:
        fee = Asset.hive(HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION)

        return ClaimAccountOperation(creator=self.owner, fee=fee)
