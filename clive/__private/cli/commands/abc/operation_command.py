from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand

if TYPE_CHECKING:
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.models.schemas import OperationUnion


@dataclass(kw_only=True)
class OperationCommand(PerformActionsOnTransactionCommand, ABC):
    """
    Class for commands that create operations.

    Args:
        sign: The signature to use for the operation.
        force_unsign: If True, forces the operation to be unsigned, default - False.
        save_file: The file to save the operation to.
        broadcast: If True, broadcasts the operation after creation.
    """

    sign: str | None
    force_unsign: bool = field(init=False, default=False)
    save_file: str | None
    broadcast: bool

    @abstractmethod
    async def _create_operation(self) -> OperationUnion:
        """
        Get the operation to be processed.

        Returns:
            OperationUnion: The operation object.
        """

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        """
        Get the transaction content for the transaction.

        Returns:
            TransactionConvertibleType: The transaction convertible type.
        """
        return await self._create_operation()

    async def validate(self) -> None:
        """
        Validate the command.

        Returns:
            None
        """
        self._validate_if_broadcast_is_used_without_force_unsign()
        self._validate_if_broadcasting_signed_transaction()
        await super().validate()
