from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.core.ensure_transaction import TransactionConvertibleType


@dataclass(kw_only=True)
class OperationCommand(PerformActionsOnTransactionCommand, ABC):
    force_unsign: bool = field(init=False, default=False)

    @abstractmethod
    async def _create_operations(self) -> ComposeTransaction:
        """Get async generator with the operations to be processed, intended to be overridden."""
        if False:
            yield  # keeps MyPy happy that it's an async generator https://mypy.readthedocs.io/en/stable/more_types.html#asynchronous-iterators

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        return [operation async for operation in self._create_operations()]

    async def validate(self) -> None:
        self._validate_if_broadcasting_signed_transaction()
        await super().validate()
