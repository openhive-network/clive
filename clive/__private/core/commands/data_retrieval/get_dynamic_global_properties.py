from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.models.schemas import DynamicGlobalProperties

if TYPE_CHECKING:
    from clive.__private.core.node import Node


@dataclass
class GetDynamicGlobalProperties(
    CommandDataRetrieval[DynamicGlobalProperties, DynamicGlobalProperties, DynamicGlobalProperties]
):
    node: Node

    async def _harvest_data_from_api(self) -> DynamicGlobalProperties:
        return await self.node.api.database_api.get_dynamic_global_properties()
