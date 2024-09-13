from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIBothBeekeepersPasswordAndSessionTokenSetError,
    CLIEitherBeekeepersPasswordOrSessionTokenNotSetError,
    CLIWalletIsNotUnlockedError,
)
from clive.__private.settings import safe_settings


@dataclass(kw_only=True)
class WorldBasedWithPasswordOrTokenCommand(WorldBasedCommand):
    """A command that requires a world with password or session token."""

    password: str | None = None

    @property
    def password_ensure(self) -> str:
        assert self.password is not None, "Password is required at this point."
        return self.password

    def is_session_token_set(self) -> bool:
        return safe_settings.beekeeper.is_session_token_set

    async def validate(self) -> None:
        self._validate_no_both_credentials_given()
        self._validate_password_or_session_token_set()
        await super().validate()

    async def _configure(self) -> None:
        self.use_beekeeper = self._is_beekeeper_required()
        await super()._configure()

    async def validate_inside_context_manager(self) -> None:
        self._validate_if_wallet_is_unlocked()
        await super().validate_inside_context_manager()

    async def _configure_inside_context_manager(self) -> None:
        if self._is_beekeeper_required():
            await self._configure_wallet()
        await super()._configure_inside_context_manager()

    async def _configure_wallet(self) -> None:
        if self.password and not self.is_session_token_set():
            await self.world.commands.unlock(password=self.password_ensure)

    def _validate_if_wallet_is_unlocked(self) -> None:
        if not self._is_beekeeper_required():
            return

        if self.is_session_token_set() and not self.world.app_state.is_unlocked:
            raise CLIWalletIsNotUnlockedError(self.world.profile.name)

    def _validate_no_both_credentials_given(self) -> None:
        if self._is_both_password_and_session_token_set():
            raise CLIBothBeekeepersPasswordAndSessionTokenSetError

    def _validate_password_or_session_token_set(self) -> None:
        if not self._is_beekeeper_required():
            return  # Skip validation if beekeeper is not required

        if not self._credentials_provided():
            raise CLIEitherBeekeepersPasswordOrSessionTokenNotSetError

    def _is_both_password_and_session_token_set(self) -> bool:
        return self.password is not None and self.is_session_token_set()

    def _credentials_provided(self) -> bool:
        return bool(self.password) or self.is_session_token_set()

    def _is_beekeeper_required(self) -> bool:
        """Override in child class to provide own logic."""
        return True
