from abc import ABC, abstractmethod
from dataclasses import dataclass

from clive.__private.cli.commands.abc.perform_transaction_command import PerformTransactionCommand
from clive.models import Operation


@dataclass(kw_only=True)
class OperationCommand(PerformTransactionCommand, ABC):
    @abstractmethod
    def _get_content(self) -> Operation:
        """Should return the operation to be converted to a transaction."""
