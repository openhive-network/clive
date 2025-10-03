from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class CommandBase[T](ABC):
    async def validate(self) -> None:  # noqa: B027
        pass

    @abstractmethod
    async def _run(self) -> T:
        """Run the command logic."""

    async def run(self) -> T:
        await self.validate()
        return await self._run()


class CommandBaseSync[T](ABC):
    def validate(self) -> None:  # noqa: B027
        pass

    @abstractmethod
    def _run(self) -> T:
        """Run the command logic."""

    def run(self) -> T:
        self.validate()
        return self._run()
