from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import cast

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrivateKeyInMemoValidationError
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.validators.private_key_in_memo_validator import PrivateKeyInMemoValidator


@dataclass(kw_only=True)
class MemoCommand(WorldBasedCommand, ABC):
    memo: str | None

    @property
    def ensure_memo(self) -> str:
        memo = self.memo
        assert self.is_option_given(memo)
        return cast("str", memo)

    async def fetch_data(self) -> None:
        await super().fetch_data()
        await self.world.commands.update_node_data(accounts=self.profile.accounts.tracked)

    async def validate_inside_context_manager(self) -> None:
        self._validate_private_key_in_memo(self.ensure_memo)
        await super().validate_inside_context_manager()

    def _validate_private_key_in_memo(self, memo_value: str) -> None:
        memo_validator = PrivateKeyInMemoValidator(self.world)
        result = memo_validator.validate(value=memo_value)
        if not result.is_valid:
            raise CLIPrivateKeyInMemoValidationError(humanize_validation_result(result))
