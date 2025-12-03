from __future__ import annotations

from abc import ABC

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.validators.private_key_in_memo_validator import PrivateKeyInMemoValidator


class MemoCommand(WorldBasedCommand, ABC):
    async def validate_memo(self, memo_value: str) -> None:
        world = self.world
        account_manager = self.profile.accounts
        await world.commands.update_node_data(accounts=account_manager.tracked)
        memo_validator = PrivateKeyInMemoValidator(world.wax_interface, account_manager)
        result = memo_validator.validate(memo_value=memo_value)
        if not result.is_valid:
            raise typer.BadParameter("Private key detected in provided memo.")
