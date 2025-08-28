from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

import typer

from clive.__private.cli.cli_world import CLIWorld
from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
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
from clive.__private.core.world import World
from clive.__private.settings import safe_settings

if TYPE_CHECKING:
    from beekeepy.interfaces import HttpUrl

    from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class WorldBasedCommand(ContextualCLICommand[World], ABC):
    """A command that requires a world and session token."""

    @property
    def world(self) -> World:
        return self._context_manager_instance

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
    def should_validate_if_remote_address_required(self) -> bool:
        return True

    @property
    def should_validate_if_session_token_required(self) -> bool:
        return True

    @property
    def should_require_unlocked_wallet(self) -> bool:
        return True

    async def validate(self) -> None:
        if self.should_validate_if_remote_address_required:
            self._validate_beekeeper_remote_address_set()
        if self.should_validate_if_session_token_required:
            self._validate_beekeeper_session_token_set()
        await self._validate_remote_beekeeper_running()
        await super().validate()

    async def validate_inside_context_manager(self) -> None:
        await super().validate_inside_context_manager()

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
            self._validate_if_wallet_is_unlocked()
            self._supply_with_correct_default_for_working_account(self.profile)

    def _print_launching_beekeeper(self) -> None:
        message = (
            "Launching beekeeper..."
            if not self.beekeeper_remote_url
            else f"Using beekeeper at {self.beekeeper_remote_url}"
        )

        typer.echo(message)
