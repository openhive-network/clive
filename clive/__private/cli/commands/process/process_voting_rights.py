from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import DeclineVotingRightsOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction


@dataclass(kw_only=True)
class _ProcessVotingRightsCommon(OperationCommand):
    account_name: str


@dataclass(kw_only=True)
class ProcessVotingRightsDecline(_ProcessVotingRightsCommon):
    async def _create_operations(self) -> ComposeTransaction:
        yield DeclineVotingRightsOperation(
            account=self.account_name,
            decline=True,
        )


@dataclass(kw_only=True)
class ProcessVotingRightsCancelDecline(_ProcessVotingRightsCommon):
    async def _create_operations(self) -> ComposeTransaction:
        yield DeclineVotingRightsOperation(
            account=self.account_name,
            decline=False,
        )
