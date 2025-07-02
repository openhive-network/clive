from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, field
from typing import Any

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand


@dataclass(kw_only=True)
class ContextualCLICommand[AsyncContextManagerT: AbstractAsyncContextManager[Any]](ExternalCLICommand, ABC):
    """A command that has to be run inside some context manager (so has some preparation)."""

    __context_manager_instance: AsyncContextManagerT | None = field(default=None, init=False)

    @property
    def _context_manager_instance(self) -> AsyncContextManagerT:
        """
        Get the context manager instance that will be used to run the command.

        Returns:
            AsyncContextManagerT: The context manager instance.
        """
        assert self.__context_manager_instance is not None, "Context manager should be set before running the command."
        return self.__context_manager_instance

    @abstractmethod
    async def _create_context_manager_instance(self) -> AsyncContextManagerT:
        """
        Create the context manager that will be used to run the command.

        Returns:
            AsyncContextManagerT: The context manager instance that will be used to run the command.

        """

    async def validate_inside_context_manager(self) -> None:
        """
        Validate the command inside the context manager.

        If the command is invalid, raise an CLIPrettyError (or it's derivative) exception.

        Raises:
            CLIPrettyError: If the command is invalid

        Returns:
            None
        """
        return

    async def _configure_inside_context_manager(self) -> None:
        """
        Configure the command before running.

        Returns:
            None
        """
        return

    async def fetch_data(self) -> None:
        """
        Fetch data.

        Returns:
            None
        """
        return

    async def _hook_before_entering_context_manager(self) -> None:
        """
        Additional hook called before entering the context manager.

        Returns:
            None
        """
        return

    async def _hook_after_entering_context_manager(self) -> None:
        """
        Additional hook called after entering the context manager.

        Returns:
            None
        """
        return

    async def run(self) -> None:
        """
        Run the command.

        Returns:
            None
        """
        if not self._skip_validation:
            await self.validate()
        await self._configure()
        await self._run_in_context_manager()

    async def _run_in_context_manager(self) -> None:
        """
        Run the command inside the context manager, handling hooks and setup.

        Returns:
            None
        """
        self.__context_manager_instance = await self._create_context_manager_instance()

        await self._hook_before_entering_context_manager()
        async with self._context_manager_instance:
            await self._hook_after_entering_context_manager()
            await self.fetch_data()
            if not self._skip_validation:
                await self.validate_inside_context_manager()
            await self._configure_inside_context_manager()
            await self._run()
