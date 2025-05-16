from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperRemoteAddressIsNotRespondingError,
    CLIBeekeeperRemoteAddressIsNotSetError,
    CLIBeekeeperSessionTokenNotSetError,
    CLINoProfileUnlockedError,
    CLIPrettyError,
    CLISessionNotLockedError,
)
from clive.__private.core.accounts.exceptions import AccountNotFoundError
from clive.__private.core.commands.get_wallet_names import GetWalletNames
from clive.__private.core.url_utils import is_url_reachable
from clive.__private.core.world import CLIWorld, World
from clive.__private.settings import safe_settings

if TYPE_CHECKING:
    from beekeepy.interfaces import HttpUrl

    from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class WorldBasedCommand(ExternalCLICommand, ABC):
    """A command that requires a world and beekeeper remote address."""

    _world: World | None = field(default=None, init=False)

    @property
    def world(self) -> World:
        assert self._world is not None, "World should be set before running the command."
        return self._world

    @property
    def profile(self) -> Profile:
        return self.world.profile

    @property
    def beekeeper_remote_url(self) -> HttpUrl | None:
        return safe_settings.beekeeper.remote_address

    @property
    def is_session_token_set(self) -> bool:
        return safe_settings.beekeeper.is_session_token_set

    @property
    def should_validate_if_session_token_required(self) -> bool:
        return True

    @property
    def should_require_unlocked_wallet(self) -> bool:
        return True

    async def validate(self) -> None:
        self._validate_beekeeper_remote_address_set()
        if self.should_validate_if_session_token_required:
            self._validate_beekeeper_session_token_set()
        await self._validate_remote_beekeeper_running()
        await super().validate()

    async def validate_inside_context_manager(self) -> None:
        """
        Validate the command inside the context manager.

        If the command is invalid, raise an CLIPrettyError (or it's derivative) exception.

        Raises
        ------
        CLIPrettyError: If the command is invalid.
        """
        return

    async def _configure_inside_context_manager(self) -> None:
        """Configure the command before running."""
        return

    async def fetch_data(self) -> None:
        """Fetch data."""
        return

    def _validate_beekeeper_remote_address_set(self) -> None:
        if self.beekeeper_remote_url is None:
            raise CLIBeekeeperRemoteAddressIsNotSetError

    def _validate_beekeeper_session_token_set(self) -> None:
        if not safe_settings.beekeeper.is_session_token_set:
            raise CLIBeekeeperSessionTokenNotSetError

    async def _validate_remote_beekeeper_running(self) -> None:
        beekeeper_remote_url = self.beekeeper_remote_url
        if beekeeper_remote_url and not await is_url_reachable(beekeeper_remote_url):
            raise CLIBeekeeperRemoteAddressIsNotRespondingError(beekeeper_remote_url)

    async def _validate_session_is_locked(self) -> None:
        unlocked_wallet_names = await GetWalletNames(
            session=await self.world.beekeeper_manager.beekeeper.session, filter_by_status="unlocked"
        ).execute_with_result()

        if unlocked_wallet_names:
            raise CLISessionNotLockedError

    def _validate_if_wallet_is_unlocked(self) -> None:
        if not self.world.app_state.is_unlocked:
            raise CLINoProfileUnlockedError

    def _validate_session_token_set(self) -> None:
        if not self.is_session_token_set:
            raise CLIBeekeeperSessionTokenNotSetError

    def _validate_account_exists(self, account_name: str) -> None:
        try:
            self.profile.accounts.get_tracked_account(account_name)
        except AccountNotFoundError as ex:
            raise CLIPrettyError(str(ex)) from None

    async def _create_context_manager_instance(self) -> World:
        return CLIWorld()

    async def _hook_before_entering_context_manager(self) -> None:
        self._print_launching_beekeeper()

    async def _hook_after_entering_context_manager(self) -> None:
        if self.should_require_unlocked_wallet:
            self._supply_with_correct_default_for_working_account(self.profile)

    def _print_launching_beekeeper(self) -> None:
        message = (
            "Launching beekeeper..."
            if not self.beekeeper_remote_url
            else f"Using beekeeper at {self.beekeeper_remote_url}"
        )

        typer.echo(message)

    async def run(self) -> None:
        if not self._skip_validation:
            await self.validate()
        await self._configure()
        await self._run_in_context_manager()

    async def _run_in_context_manager(self) -> None:
        self._world = await self._create_context_manager_instance()

        await self._hook_before_entering_context_manager()
        async with self._world:
            if self.should_require_unlocked_wallet:
                self._validate_if_wallet_is_unlocked()
            await self._hook_after_entering_context_manager()
            await self.fetch_data()
            if not self._skip_validation:
                await self.validate_inside_context_manager()
            await self._configure_inside_context_manager()
            await self._run()
