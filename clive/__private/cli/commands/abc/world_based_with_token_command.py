from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperSessionTokenNotSetError,
    CLIWalletIsNotUnlockedError,
)
from clive.__private.settings import safe_settings


@dataclass(kw_only=True)
class WorldBasedWithTokenCommand(WorldBasedCommand):
    """A command that requires a world with session token."""

    def is_session_token_set(self) -> bool:
        return safe_settings.beekeeper.is_session_token_set

    async def validate(self) -> None:
        self._validate_session_token_set()
        await super().validate()

    async def _configure(self) -> None:
        self.use_beekeeper = self._is_beekeeper_required()
        await super()._configure()

    async def validate_inside_context_manager(self) -> None:
        self._validate_if_wallet_is_unlocked()
        await super().validate_inside_context_manager()

    def _validate_if_wallet_is_unlocked(self) -> None:
        if not self._is_beekeeper_required():
            return

        if self.is_session_token_set() and not self.world.app_state.is_unlocked:
            raise CLIWalletIsNotUnlockedError(self.world.profile.name)

    def _validate_session_token_set(self) -> None:
        if not self._is_beekeeper_required():
            return  # Skip validation if beekeeper is not required

        if not self.is_session_token_set():
            raise CLIBeekeeperSessionTokenNotSetError

    def _is_beekeeper_required(self) -> bool:
        """Override in child class to provide own logic."""
        return True
