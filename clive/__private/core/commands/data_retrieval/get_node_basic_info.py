from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, get_args

from typing_extensions import TypeGuard

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node
    from clive.models.aliased import Config, DynamicGlobalProperties, Version


NetworkType = Literal["mainnet", "testnet", "mirrornet"]


def _is_known_network_type_literal(value: str) -> TypeGuard[NetworkType]:
    return value in get_args(NetworkType)


@dataclass
class NodeBasicInfoData:
    config: Config
    version: Version
    dynamic_global_properties: DynamicGlobalProperties

    @property
    def network_type(self) -> NetworkType:
        network_type = self.version.node_type
        if _is_known_network_type_literal(network_type):
            return network_type

        raise AssertionError(f"Unknown node type: {self.version.node_type}, expected one of: {NetworkType}")

    @property
    def chain_id(self) -> str:
        return self.config.HIVE_CHAIN_ID


@dataclass
class GetNodeBasicInfo(CommandDataRetrieval[NodeBasicInfoData, NodeBasicInfoData, NodeBasicInfoData]):
    node: Node

    async def _harvest_data_from_api(self) -> NodeBasicInfoData:
        async with self.node.batch() as node:
            return NodeBasicInfoData(
                config=await node.api.database_api.get_config(),
                version=await node.api.database_api.get_version(),
                dynamic_global_properties=await node.api.database_api.get_dynamic_global_properties(),
            )
