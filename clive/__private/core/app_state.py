from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive.models.aliased import DynamicGlobalProperties


@dataclass
class AppState:
    """A class that holds information about the current state of an application."""

    world: World
    _is_active: bool = False
    _dynamic_global_properties: DynamicGlobalProperties | None = None

    async def get_dynamic_global_properties(self) -> DynamicGlobalProperties:
        if self._dynamic_global_properties is None:
            (await self.world.commands.update_node_data()).raise_if_error_occurred()
        assert self._dynamic_global_properties is not None
        return self._dynamic_global_properties

    @property
    async def is_active(self) -> bool:
        return self._is_active

    def activate(self) -> None:
        self._is_active = True
        logger.info("Mode switched to ACTIVE.")

    def deactivate(self) -> None:
        self._is_active = False
        logger.info("Mode switched to INACTIVE.")

    def __hash__(self) -> int:
        return id(self.world)
