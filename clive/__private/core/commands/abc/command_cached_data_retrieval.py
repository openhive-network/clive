from __future__ import annotations

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_data_retrieval_base import (
    CommandDataRetrievalBase,
    HarvestedDataT,
    SanitizedDataT,
)


class CommandCachedDataRetrieval(Command, CommandDataRetrievalBase[HarvestedDataT, SanitizedDataT, None]):
    async def _execute(self) -> None:
        await super()._perform_data_operations()
