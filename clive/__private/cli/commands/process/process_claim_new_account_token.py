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
    """
    Class to process a claim new account token operation.

    Args:
        creator: The account name of the creator.
        fee: The fee for the operation. If None, resource credits will be used instead of Hive.
    """

    creator: str
    fee: Asset.Hive | None
    """None means RC will be used instead of payment in Hive"""

    async def _create_operation(self) -> ClaimAccountOperation:
        """
        Create an instance based on the provided creator and fee.

        Returns:
            ClaimAccountOperation: An operation instance with the specified creator and fee.
        """
        if self.fee == HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION_ASSET:
            raise CLIClaimAccountTokenZeroFeeError
        fee = self.fee if self.fee is not None else HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION_ASSET.copy()

        return ClaimAccountOperation(creator=self.creator, fee=fee)


class CLIClaimAccountTokenZeroFeeError(CLIPrettyError):
    """Class to handle errors when the fee for claiming a new account token is zero."""

    def __init__(self) -> None:
        """
        Initialize the error with a specific message and error number.

        Returns:
            None
        """
        message = "Fee can't be zero, to use resource credits skip the fee option."
        super().__init__(message, errno.E2BIG)
