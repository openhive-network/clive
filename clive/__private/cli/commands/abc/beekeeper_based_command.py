from abc import ABC
from dataclasses import dataclass

import typer
from beekeepy import AsyncBeekeeper
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
class BeekeeperCommon:
    @property
    def beekeeper_remote_url(self) -> HttpUrl | None:
        """
        Select Beekeeper's remote URL address.

        If `CLIVE_BEEKEEPER_REMOTE_ADDRESS` environment variable is set, that address will be used.
        Otherwise value from settings will be used.
        """
        if safe_settings.beekeeper.is_remote_address_set:
            return safe_settings.beekeeper.remote_address
        return None

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
        # in WorldBasedCommand, should not be exposed as Commands should be used instead
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

    async def validate_session_is_locked(self) -> None:
        unlocked_wallet_names = await GetWalletNames(
            session=await self.beekeeper.session, filter_by_status="unlocked"
        ).execute_with_result()
        if unlocked_wallet_names:
            raise CLISessionNotLockedError

    async def _create_context_manager_instance(self) -> AsyncBeekeeper:
        return await (
            AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory())
            if safe_settings.beekeeper.should_start_locally
            else AsyncBeekeeper.remote_factory(url_or_settings=safe_settings.beekeeper.settings_remote_factory())
        )

    async def _hook_before_entering_context_manager(self) -> None:
        self._print_launching_beekeeper()
