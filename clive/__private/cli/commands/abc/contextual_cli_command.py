from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand

AsyncContextManagerType = TypeVar("AsyncContextManagerType", bound=Any)


@dataclass(kw_only=True)
class ContextualCLICommand(Generic[AsyncContextManagerType], ExternalCLICommand, ABC):
    """A command that has to be run inside some context manager (so has some preparation)."""

    __context_manager_instance: AsyncContextManagerType | None = field(default=None, init=False)

    @property
    def _context_manager_instance(self) -> AsyncContextManagerType:
        assert self.__context_manager_instance is not None, "Context manager should be set before running the command."
        return self.__context_manager_instance

    @abstractmethod
    async def _create_context_manager_instance(self) -> AsyncContextManagerType:
        """Create the context manager that will be used to run the command."""

    async def validate_inside_context_manager(self) -> None:
        """
        Validate the command inside the context manager.

        If the command is invalid, raise an CLIPrettyError (or it's derivative) exception.

        Raises
        ------
        CLIPrettyError: If the command is invalid.
        """
        return

    async def _hook_before_entering_context_manager(self) -> None:
        """Additional hook called before entering the context manager."""
        return

    async def run(self) -> None:
        if not self._skip_validation:
            await self.validate()
        await self._configure()
        await self._run_in_context_manager()

    async def _run_in_context_manager(self) -> None:
        self.__context_manager_instance = await self._create_context_manager_instance()

        await self._hook_before_entering_context_manager()
        async with self._context_manager_instance:
            if not self._skip_validation:
                await self.validate_inside_context_manager()
            await self._run()
