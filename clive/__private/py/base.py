from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn, Self, override

from clive.__private.before_launch import prepare_before_launch
from clive.__private.core.world import World
from clive.__private.py.configure import ConfigureInterface
from clive.__private.py.exceptions import PyContextManagerNotUsedError
from clive.__private.py.generate import GenerateInterface
from clive.__private.py.show import ShowInterface, ShowInterfaceNoProfile

if TYPE_CHECKING:
    from types import TracebackType


class PyWorld(World):
    """
    World specialized for Python Interface (PY) usage.

    Automatically loads unlocked profile during setup, similar to CLIWorld and TUIWorld.
    This ensures that PY operations always have access to a loaded profile.
    """

    @override
    async def _setup(self) -> None:
        await super()._setup()
        await self.load_profile_based_on_beekepeer()


def clive_use_unlocked_profile() -> UnlockedClivePy:
    """
    Factory function to create a Clive PY instance with an unlocked profile.

    IMPORTANT: UnlockedClivePy MUST be used as an async context manager (with 'async with' statement).
    This ensures proper initialization (profile loading) and cleanup (profile saving).

    Returns:
        UnlockedClivePy instance configured to use an already unlocked profile.

    Example:
        async with clive_use_unlocked_profile() as clive:
            balances = await clive.show.balances("alice")
    """
    return UnlockedClivePy()


class ClivePy:
    """
    Main entry point for Clive Python Interface without profile context.

    Provides access to read-only operations that don't require a profile.
    For operations requiring a profile, use UnlockedClivePy instead.

    Example:
        async with ClivePy() as clive:
            profiles = await clive.show.profiles()
    """

    def __init__(self) -> None:
        self.show = ShowInterfaceNoProfile()
        self.generate = GenerateInterface()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        pass


class UnlockedClivePy:
    """
    Clive Python Interface with profile context.

    This class provides full access to Clive functionality including operations
    that require an unlocked profile (show balances, accounts, witnesses, etc.).

    IMPORTANT: This class MUST be used as an async context manager (with 'async with' statement).
    The context manager ensures:
    - Profile is automatically loaded from the unlocked beekeeper wallet on entry (__aenter__)
    - Profile is automatically saved to storage on exit (__aexit__)
    - Proper cleanup of resources (node, wax interface, beekeeper)

    Use the factory function or context manager:
        async with clive_use_unlocked_profile() as clive:
            balances = await clive.show.balances("alice")

    Or directly:
        async with UnlockedClivePy() as clive:
            accounts = await clive.show.accounts()

    Note: Process operations (transfer, update_authority, etc.) will be available in a future release.
    """

    def __init__(self) -> None:
        self._world = PyWorld()
        self._is_setup_called = False
        self.__show = ShowInterface(self)
        self.__configure = ConfigureInterface(self)
        self.generate = GenerateInterface()
        self.__prepare_before_launch()

    async def __aenter__(self) -> Self:
        await self.setup()
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.close()

    @property
    def show(self) -> ShowInterface:
        """Access to show operations. Requires context manager to be entered."""
        self._ensure_setup_called()
        return self.__show

    @property
    def process(self) -> NoReturn:
        """
        Access to process operations (transfer, update_authority, etc.).

        NOTE: Process operations are not yet implemented in this release.
        They will be available in a future release.

        Raises:
            NotImplementedError: Always, as process operations are not yet available.
        """
        raise NotImplementedError(
            "Process operations (transfer, update_authority, transaction, etc.) are not yet available. "
            "They will be added in a future release."
        )

    @property
    def configure(self) -> ConfigureInterface:
        """Access to configure operations. Requires context manager to be entered."""
        self._ensure_setup_called()
        return self.__configure

    async def setup(self) -> None:
        """Initialize the PY world and load profile. Called automatically by context manager."""
        await self._world.setup()
        self._is_setup_called = True

    async def close(self) -> None:
        """Cleanup resources and save profile. Called automatically by context manager."""
        await self._world.close()

    def __prepare_before_launch(self) -> None:
        prepare_before_launch()

    def _ensure_setup_called(self) -> None:
        """Ensure setup was called by checking if context manager was used."""
        if not self._is_setup_called:
            raise PyContextManagerNotUsedError(
                "UnlockedClivePy must be used as an async context manager. "
                "Use 'async with UnlockedClivePy() as clive:' or 'async with clive_use_unlocked_profile() as clive:'"
            )
