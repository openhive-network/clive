from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.models.schemas import WitnessSchedule

if TYPE_CHECKING:
    from clive.__private.core.node import Node


@dataclass(kw_only=True)
class GetWitnessSchedule(CommandDataRetrieval[WitnessSchedule, WitnessSchedule, WitnessSchedule]):
    node: Node

    async def _harvest_data_from_api(self) -> WitnessSchedule:
        return await self.node.api.database_api.get_witness_schedule()
