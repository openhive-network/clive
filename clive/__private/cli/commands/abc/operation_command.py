from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand
from clive.__private.core.ensure_transaction import TransactionConvertibleType
from clive.__private.models.schemas import OperationUnion


@dataclass(kw_only=True)
class OperationCommand(PerformActionsOnTransactionCommand, ABC):
    password: str | None
    sign: str | None
    force_unsign: bool = field(init=False, default=False)
    save_file: str | None
    broadcast: bool

    @abstractmethod
    async def _create_operation(self) -> OperationUnion:
        """Get the operation to be processed."""

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        return await self._create_operation()

    async def validate(self) -> None:
        self._validate_broadcast_sign_password_token()
        await super().validate()
