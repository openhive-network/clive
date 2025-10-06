from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.models.schemas import FindWitnesses, Witness

if TYPE_CHECKING:
    from clive.__private.core.node import Node


class WitnessNotFoundError(CommandError):
    def __init__(self, command: Command, witness_name: str) -> None:
        super().__init__(command, f"Witness '{witness_name}' was not found.")


@dataclass(kw_only=True)
class FindWitness(CommandWithResult[Witness]):
    node: Node
    witness_name: str

    async def _execute(self) -> None:
        response: FindWitnesses = await self.node.api.database_api.find_witnesses(owners=[self.witness_name])
        if len(response.witnesses) == 0:
            raise WitnessNotFoundError(self, self.witness_name)
        first_witness = response.witnesses[0]
        assert first_witness.owner == self.witness_name
        self._result = first_witness
