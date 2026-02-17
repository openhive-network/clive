from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.core.constants.authority import (
    DEFAULT_AUTHORITY_THRESHOLD,
    DEFAULT_AUTHORITY_WEIGHT,
)
from clive.__private.models.schemas import Authority, RequestAccountRecoveryOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.core.keys.keys import PublicKey


@dataclass(kw_only=True)
class ProcessRequestAccountRecovery(OperationCommand):
    recovery_account: str
    account_to_recover: str
    new_owner_key: PublicKey

    async def _create_operations(self) -> ComposeTransaction:
        new_owner_authority = Authority(
            weight_threshold=DEFAULT_AUTHORITY_THRESHOLD,
            account_auths=[],
            key_auths=[(self.new_owner_key.value, DEFAULT_AUTHORITY_WEIGHT)],
        )
        yield RequestAccountRecoveryOperation(
            recovery_account=self.recovery_account,
            account_to_recover=self.account_to_recover,
            new_owner_authority=new_owner_authority,
        )
