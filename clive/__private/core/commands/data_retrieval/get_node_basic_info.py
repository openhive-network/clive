from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beekeepy.exceptions import UnknownDecisionPathError

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.__private.models.schemas import Config, DynamicGlobalProperties, Version


@dataclass
class NodeBasicInfoData:
    config: Config
    version: Version
    dynamic_global_properties: DynamicGlobalProperties

    @property
    def network_type(self) -> str:
        return self.version.node_type

    @property
    def chain_id(self) -> str:
        return self.config.HIVE_CHAIN_ID


@dataclass
class GetNodeBasicInfo(CommandDataRetrieval[NodeBasicInfoData, NodeBasicInfoData, NodeBasicInfoData]):
    node: Node

    async def _harvest_data_from_api(self) -> NodeBasicInfoData:
        async with await self.node.batch() as node:
            return NodeBasicInfoData(
                config=await node.api.database_api.get_config(),
                version=await node.api.database_api.get_version(),
                dynamic_global_properties=await node.api.database_api.get_dynamic_global_properties(),
            )

        raise UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")
