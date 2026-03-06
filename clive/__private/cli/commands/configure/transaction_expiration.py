from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta  # noqa: TC003

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIInvalidTransactionExpirationError
from clive.__private.core.profile import InvalidTransactionExpirationError


@dataclass(kw_only=True)
class SetTransactionExpiration(WorldBasedCommand):
    expiration: timedelta

    async def _run(self) -> None:
        try:
            self.profile.set_transaction_expiration(self.expiration)
        except InvalidTransactionExpirationError as error:
            raise CLIInvalidTransactionExpirationError(error) from None


@dataclass(kw_only=True)
class ResetTransactionExpiration(WorldBasedCommand):
    async def _run(self) -> None:
        self.profile.reset_transaction_expiration()
