from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beekeepy.exceptions import UnknownDecisionPathError
from helpy.exceptions import CommunicationError, ExceededAmountOfRetriesError

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
        dgpo = await self._safely_acquire_dynamic_global_properties()

        async with await self.node.batch() as node:
            return NodeBasicInfoData(
                config=await node.api.database_api.get_config(),
                version=await node.api.database_api.get_version(),
                dynamic_global_properties=dgpo,
            )

        raise UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _safely_acquire_dynamic_global_properties(self) -> DynamicGlobalProperties:
        error_message = "Unable to acquire database lock"
        count = 5
        while count >= 0:
            try:
                return await self.node.api.database_api.get_dynamic_global_properties()
            except CommunicationError as error:  # noqa: PERF203
                count -= 1
                if error_message not in str(error.response):
                    raise
        raise ExceededAmountOfRetriesError(url=self.node.http_endpoint, request="get_dynamic_global_properties")
