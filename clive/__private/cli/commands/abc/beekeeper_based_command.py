from abc import ABC, abstractmethod
from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperLocallyNotRunningError,
    CLIBeekeeperRemoteAddressIsNotRespondingError,
    CLIBeekeeperRemoteAddressIsNotSetError,
    CLIBeekeeperSessionTokenIsNotSetError,
    CLISessionNotLockedError,
)
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.get_wallet_names import GetWalletNames
from clive.__private.core.url import Url
from clive.__private.settings import safe_settings


@dataclass(kw_only=True)
class BeekeeperCommon(ABC):
    beekeeper_remote: str | Url | None = None
    """If None, beekeeper will be launched locally."""

    @property
    @abstractmethod
    def beekeeper(self) -> Beekeeper: ...

    @property
    def beekeeper_remote_url(self) -> Url | None:
        if self.beekeeper_remote is None:
            return None
        if isinstance(self.beekeeper_remote, Url):
            return self.beekeeper_remote
        return Url.parse(self.beekeeper_remote)

    async def validate_session_is_locked(self) -> None:
        unlocked_wallet_names = await GetWalletNames(
            beekeeper=self.beekeeper, filter_by_status="unlocked"
        ).execute_with_result()
        if unlocked_wallet_names:
            raise CLISessionNotLockedError

    async def validate_beekeeper_remote_address_set(self) -> None:
        if not safe_settings.beekeeper.is_remote_address_set:
            raise CLIBeekeeperRemoteAddressIsNotSetError

    async def validate_beekeeper_session_token_set(self) -> None:
        if not safe_settings.beekeeper.is_session_token_set:
            raise CLIBeekeeperSessionTokenIsNotSetError

    async def validate_remote_beekeeper_running(self) -> None:
        if self.beekeeper_remote_url and not await self.beekeeper_remote_url.is_url_open():
            raise CLIBeekeeperRemoteAddressIsNotRespondingError(self.beekeeper_remote_url)

    async def validate_local_beekeeper_running(self) -> None:
        if not await Beekeeper.is_already_running_locally():
            raise CLIBeekeeperLocallyNotRunningError

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

    async def _create_context_manager_instance(self) -> Beekeeper:
        return Beekeeper(remote_endpoint=self.beekeeper_remote_url)

    async def _hook_before_entering_context_manager(self) -> None:
        self._print_launching_beekeeper()
