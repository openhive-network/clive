from __future__ import annotations

import errno
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from schemas.fields.assets.hive import AssetHiveHF26
from schemas.fields.compound import LegacyChainProperties
from schemas.operations import WitnessUpdateOperation

if TYPE_CHECKING:
    from clive.models import Asset
    from schemas.fields.basic import PublicKey


@dataclass(kw_only=True)
class ProcessWitnessCreate(OperationCommand):
    owner: str
    url: str
    block_signing_key: PublicKey
    fee: Asset.Hive
    account_creation_fee: Asset.Hive
    """None means RC will be used instead of payment in Hive"""

    async def _create_operation(self) -> WitnessUpdateOperation:
        props = LegacyChainProperties[AssetHiveHF26](account_creation_fee=self.account_creation_fee)

        return WitnessUpdateOperation(
            owner=self.owner, url=self.url, block_signing_key=self.block_signing_key, fee=self.fee, props=props
        )


class CLIClaimAccountTokenZeroFeeError(CLIPrettyError):
    def __init__(self) -> None:
        message = "Fee can't be zero, to use resource credits skip the fee option."
        super().__init__(message, errno.E2BIG)
