from abc import ABC, abstractmethod
from dataclasses import dataclass

import typer
from beekeepy import AsyncBeekeeper, async_beekeeper_factory, async_beekeeper_remote_factory
from helpy import HttpUrl
from helpy._interfaces.url import Url

from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
from clive.models.aliased import Beekeeper, Session


@dataclass(kw_only=True)
class BeekeeperCommon(ABC):
    beekeeper_remote: str | HttpUrl | None = None
    """If None, beekeeper will be launched locally."""

    @property
    @abstractmethod
    def beekeeper(self) -> AsyncBeekeeper: ...

    @property
    def beekeeper_remote_url(self) -> HttpUrl | None:
        if self.beekeeper_remote is None:
            return None
        if isinstance(self.beekeeper_remote, Url):
            return self.beekeeper_remote
        return HttpUrl(self.beekeeper_remote)

    def _print_launching_beekeeper(self) -> None:
        message = (
            "Launching beekeeper..."
            if not self.beekeeper_remote_url
            else f"Using beekeeper at {self.beekeeper_remote_url}"
        )

        typer.echo(message)


@dataclass(kw_only=True)
class BeekeeperBasedCommand(ContextualCLICommand[Beekeeper], BeekeeperCommon, ABC):
    """A command that requires beekeeper to be running."""

    @property
    def beekeeper(self) -> Beekeeper:
        return self._context_manager_instance

    @property
    def session(self) -> Session:
        assert self.__session is not None
        return self.__session

    async def _create_context_manager_instance(self) -> Beekeeper:
        if self.beekeeper_remote_url is None:
            return async_beekeeper_factory()
        return async_beekeeper_remote_factory(url_or_settings=self.beekeeper_remote_url)

    async def _hook_before_entering_context_manager(self) -> None:
        self._print_launching_beekeeper()
        self.__session = await self.beekeeper.create_session()
        with self.__session:
            await super().run()
