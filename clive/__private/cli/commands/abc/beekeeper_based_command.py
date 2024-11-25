from abc import ABC, abstractmethod
from dataclasses import dataclass

import typer
from beekeepy import AsyncBeekeeper
from helpy import HttpUrl

from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperRemoteAddressIsNotSetError,
    CLIBeekeeperSessionTokenIsNotSetError,
    CLISessionNotLockedError,
)
from clive.__private.core.commands.get_wallet_names import GetWalletNames
from clive.__private.settings import safe_settings


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
        if isinstance(self.beekeeper_remote, HttpUrl):
            return self.beekeeper_remote
        return HttpUrl(self.beekeeper_remote)

    def _print_launching_beekeeper(self) -> None:
        message = (
            "Launching beekeeper..."
            if not self.beekeeper_remote_url
            else f"Using beekeeper at {self.beekeeper_remote_url}"
        )

        typer.echo(message)

    async def validate_session_is_locked(self) -> None:
        unlocked_wallet_names = await GetWalletNames(
            session=await self.beekeeper.session, filter_by_status="unlocked"
        ).execute_with_result()
        if unlocked_wallet_names:
            raise CLISessionNotLockedError

    async def validate_beekeeper_remote_address_set(self) -> None:
        if not safe_settings.beekeeper.is_remote_address_set:
            raise CLIBeekeeperRemoteAddressIsNotSetError

    async def validate_beekeeper_session_token_set(self) -> None:
        if not safe_settings.beekeeper.is_session_token_set:
            raise CLIBeekeeperSessionTokenIsNotSetError


@dataclass(kw_only=True)
class BeekeeperBasedCommand(ContextualCLICommand[AsyncBeekeeper], BeekeeperCommon, ABC):
    """A command that requires beekeeper to be running."""

    @property
    def beekeeper(self) -> AsyncBeekeeper:
        return self._context_manager_instance

    async def _create_context_manager_instance(self) -> AsyncBeekeeper:
        if self.beekeeper_remote_url is None:
            from clive.__private.cli.commands.beekeeper import BeekeeperLoadDetachedPID

            beekeeper_params = await BeekeeperLoadDetachedPID(remove_file=False, silent_fail=True).execute_with_result()
            if beekeeper_params.is_set():
                self.beekeeper_remote = beekeeper_params.endpoint
        remote_url = HttpUrl(self.beekeeper_remote_url) if self.beekeeper_remote_url is not None else None
        settings = safe_settings.beekeeper.settings_factory(remote_endpoint=remote_url)
        return await (
            AsyncBeekeeper.remote_factory(url_or_settings=settings)
            if remote_url is not None
            else AsyncBeekeeper.factory(settings=settings)
        )

    async def _hook_before_entering_context_manager(self) -> None:
        self._print_launching_beekeeper()
