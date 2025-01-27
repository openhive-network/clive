from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.__private.models.schemas import Config

if TYPE_CHECKING:
    from clive.__private.core.node import Node


@dataclass(kw_only=True)
class GetConfig(CommandDataRetrieval[Config, Config, Config]):
    node: Node

    async def _harvest_data_from_api(self) -> Config:
        return await self.node.api.database_api.get_config()
