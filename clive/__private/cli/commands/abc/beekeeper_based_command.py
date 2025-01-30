from abc import ABC, abstractmethod
from dataclasses import dataclass

import typer
from beekeepy import AsyncBeekeeper, Settings
from helpy import HttpUrl

from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperRemoteAddressIsNotRespondingError,
    CLIBeekeeperRemoteAddressIsNotSetError,
    CLIBeekeeperSessionTokenNotSetError,
    CLISessionNotLockedError,
)
from clive.__private.core.commands.get_wallet_names import GetWalletNames
from clive.__private.core.url_utils import is_url_reachable
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
        """
        Select Beekeeper's remote URL address.

        The value from the `--beekeeper-remote` flag has the highest priority.

        If the user did not pass this flag, but the `CLIVE_BEEKEEPER_REMOTE_ADDRESS`
        environment variable is set, that address will be used.
        """
        if self.beekeeper_remote is None:
            if safe_settings.beekeeper.is_remote_address_set:
                return safe_settings.beekeeper.remote_address
            return None
        if isinstance(self.beekeeper_remote, HttpUrl):
            return self.beekeeper_remote
        return HttpUrl(self.beekeeper_remote)

    async def validate_session_is_locked(self) -> None:
        unlocked_wallet_names = await GetWalletNames(
            session=await self.beekeeper.session, filter_by_status="unlocked"
        ).execute_with_result()
        if unlocked_wallet_names:
            raise CLISessionNotLockedError

    def validate_beekeeper_remote_address_set(self) -> None:
        if self.beekeeper_remote_url is None:
            raise CLIBeekeeperRemoteAddressIsNotSetError

    def validate_beekeeper_session_token_set(self) -> None:
        if not safe_settings.beekeeper.is_session_token_set:
            raise CLIBeekeeperSessionTokenNotSetError

    async def validate_remote_beekeeper_running(self) -> None:
        beekeeper_remote_url = self.beekeeper_remote_url
        if beekeeper_remote_url and not await is_url_reachable(beekeeper_remote_url):
            raise CLIBeekeeperRemoteAddressIsNotRespondingError(beekeeper_remote_url)

    def _print_launching_beekeeper(self) -> None:
        message = (
            "Launching beekeeper..."
            if not self.beekeeper_remote_url
            else f"Using beekeeper at {self.beekeeper_remote_url}"
        )

        typer.echo(message)


@dataclass(kw_only=True)
class BeekeeperBasedCommand(ContextualCLICommand[AsyncBeekeeper], BeekeeperCommon, ABC):
    """A command that requires beekeeper to be running."""

    @property
    def beekeeper(self) -> AsyncBeekeeper:
        return self._context_manager_instance

    @property
    def _is_session_token_required(self) -> bool:
        return True

    async def validate(self) -> None:
        self.validate_beekeeper_remote_address_set()
        if self._is_session_token_required:
            self.validate_beekeeper_session_token_set()
        await super().validate_remote_beekeeper_running()
        await super().validate()

    async def _create_context_manager_instance(self) -> AsyncBeekeeper:
        if self.beekeeper_remote_url is None:
            from clive.__private.core.commands.beekeeper import BeekeeperLoadDetachedPID

            beekeeper_params = await BeekeeperLoadDetachedPID(remove_file=False, silent_fail=True).execute_with_result()
            if beekeeper_params.is_set():
                self.beekeeper_remote = beekeeper_params.endpoint
        remote_url = HttpUrl(self.beekeeper_remote_url) if self.beekeeper_remote_url is not None else None
        settings = safe_settings.beekeeper.settings_factory(settings_to_update=Settings(http_endpoint=remote_url))
        return await (
            AsyncBeekeeper.remote_factory(url_or_settings=settings)
            if remote_url is not None
            else AsyncBeekeeper.factory(settings=settings)
        )

    async def _hook_before_entering_context_manager(self) -> None:
        self._print_launching_beekeeper()
