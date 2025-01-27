from abc import ABC
from dataclasses import dataclass

from beekeepy import AsyncBeekeeper

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperCommon
from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperSessionTokenNotSetError,
    CLINoProfileUnlockedError,
    CLIPrettyError,
)
from clive.__private.core.accounts.exceptions import AccountNotFoundError
from clive.__private.core.profile import Profile
from clive.__private.core.world import CLIWorld, World
from clive.__private.settings import safe_settings


@dataclass(kw_only=True)
class WorldBasedCommand(ContextualCLICommand[World], BeekeeperCommon, ABC):
    """A command that requires a world and session token."""

    @property
    def world(self) -> World:
        return self._context_manager_instance

    @property
    def profile(self) -> Profile:
        return self.world.profile

    @property
    def beekeeper(self) -> AsyncBeekeeper:
        return self.world.beekeeper

    def is_session_token_set(self) -> bool:
        return safe_settings.beekeeper.is_session_token_set

    async def validate(self) -> None:
        self.validate_beekeeper_remote_address_set()
        self.validate_beekeeper_session_token_set()
        await self.validate_remote_beekeeper_running()
        await super().validate()

    async def validate_inside_context_manager(self) -> None:
        self._validate_if_wallet_is_unlocked()
        await super().validate_inside_context_manager()

    def _validate_if_wallet_is_unlocked(self) -> None:
        if not self.world.app_state.is_unlocked:
            raise CLINoProfileUnlockedError

    def _validate_session_token_set(self) -> None:
        if not self.is_session_token_set():
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
        self._supply_with_correct_default_for_working_account(self.profile)
