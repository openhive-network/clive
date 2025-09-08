from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand

if TYPE_CHECKING:
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.models.schemas import OperationUnion


@dataclass(kw_only=True)
class OperationCommand(PerformActionsOnTransactionCommand, ABC):
    force_unsign: bool = field(init=False, default=False)

    @abstractmethod
    async def _create_operation(self) -> OperationUnion:
        """Get the operation to be processed."""

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        return await self._create_operation()

    def modify_common_options(
        self,
        *,
        sign_with: str | None = None,
        autosign: bool | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> None:
        is_sign_with_given = sign_with is not None
        is_broadcast_given = broadcast is not None
        is_save_file_given = save_file is not None
        is_autosign_given = autosign is not None

        if is_sign_with_given:
            self.sign_with = sign_with

        if is_broadcast_given:
            self.broadcast = cast("bool", broadcast)

        if is_save_file_given:
            self.save_file = save_file

        if is_autosign_given:
            self.autosign = cast("bool", autosign)

    async def validate(self) -> None:
        self._validate_if_broadcasting_signed_transaction()
        await super().validate()
