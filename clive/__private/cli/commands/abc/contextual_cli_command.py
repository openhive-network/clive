from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand

AsyncContextManagerType = TypeVar("AsyncContextManagerType", bound=Any)


@dataclass(kw_only=True)
class ContextualCLICommand(Generic[AsyncContextManagerType], ExternalCLICommand, ABC):
    """A command that might(!) require some preparation before running."""

    __context_manager_instance: AsyncContextManagerType | None = field(default=None, init=False)

    @property
    def _context_manager_instance(self) -> AsyncContextManagerType:
        assert self.__context_manager_instance is not None, "Context manager should be set before running the command."
        return self.__context_manager_instance

    @abstractmethod
    async def _create_context_manager_instance(self) -> AsyncContextManagerType:
        """Create the context manager that will be used to run the command."""

    @abstractmethod
    async def _run(self) -> None:
        """The actual implementation of the command."""

    async def _should_run_in_context_manager(self) -> bool:
        """A flag indicating whether the command should be prepared before running."""
        return True

    async def run(self) -> None:
        if not self._skip_validation:
            await self.validate()

        if await self._should_run_in_context_manager():
            await self._run_in_context_manager()
        else:
            await self._run()

    async def _run_in_context_manager(self) -> None:
        self.__context_manager_instance = await self._create_context_manager_instance()

        async with self._context_manager_instance:
            await self._run()
