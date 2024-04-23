from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.models.aliased import Config as SchemasConfig

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node


@dataclass(kw_only=True)
class GetConfig(CommandWithResult[SchemasConfig]):
    node: Node

    async def _execute(self) -> None:
        response: SchemasConfig = await self.node.api.database_api.get_config()
        self._result = response
