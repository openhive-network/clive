from __future__ import annotations

from clive.__private.core.commands.abc.command_data_retrieval_base import (
    CommandDataRetrievalBase,
    HarvestedDataT,
    SanitizedDataT,
)
from clive.__private.core.commands.abc.command_with_result import CommandResultT, CommandWithResult


class CommandDataRetrieval(
    CommandDataRetrievalBase[HarvestedDataT, SanitizedDataT, CommandResultT],
    CommandWithResult[CommandResultT],
):
    async def _execute(self) -> None:
        result = await super()._perform_data_operations()
        self._result = result
