from __future__ import annotations

import errno
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.constants.node_special_assets import HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION_ASSET
from clive.__private.models.schemas import ClaimAccountOperation

if TYPE_CHECKING:
    from clive.__private.models import Asset


@dataclass(kw_only=True)
class ProcessClaimNewAccountToken(OperationCommand):
    creator: str
    fee: Asset.Hive | None
    """None means RC will be used instead of payment in Hive"""

    async def _create_operation(self) -> ClaimAccountOperation:
        if self.fee == HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION_ASSET:
            raise CLIClaimAccountTokenZeroFeeError
        fee = self.fee if self.fee is not None else HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION_ASSET.copy()

        return ClaimAccountOperation(creator=self.creator, fee=fee)


class CLIClaimAccountTokenZeroFeeError(CLIPrettyError):
    def __init__(self) -> None:
        message = "Fee can't be zero, to use resource credits skip the fee option."
        super().__init__(message, errno.E2BIG)
