from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class CommandBase[T](ABC):
    async def validate(self) -> None:  # noqa: B027
        pass

    async def run(self) -> T:
        await self.validate()
        return await self._run()

    @abstractmethod
    async def _run(self) -> T:
        """Run the command logic."""
