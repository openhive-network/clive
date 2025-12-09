from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

from clive.__private.before_launch import prepare_before_launch
from clive.__private.core.world import World
from clive.__private.si.configure import ConfigureInterface
from clive.__private.si.exceptions import SIContextManagerNotUsedError
from clive.__private.si.generate import GenerateInterface
from clive.__private.si.process import ProfileOperationsInterface
from clive.__private.si.show import ShowInterface, ShowInterfaceNoProfile

if TYPE_CHECKING:
    from types import TracebackType


class SIWorld(World):
    """
    World specialized for Script Interface (SI) usage.

    Automatically loads unlocked profile during setup, similar to CLIWorld and TUIWorld.
    This ensures that SI operations always have access to a loaded profile.
    """

    @override
    async def _setup(self) -> None:
        await super()._setup()
        await self.load_profile_based_on_beekepeer()


def clive_use_unlocked_profile() -> UnlockedCliveSi:
    """
    Factory function to create a Clive SI instance with an unlocked profile.

    IMPORTANT: UnlockedCliveSi MUST be used as an async context manager (with 'async with' statement).
    This ensures proper initialization (profile loading) and cleanup (profile saving).

    Returns:
        UnlockedCliveSi instance configured to use an already unlocked profile.

    Example:
        async with clive_use_unlocked_profile() as clive:
            await clive.process.transfer(...).broadcast()
    """
    return UnlockedCliveSi()


class CliveSi:
    """
    Main entry point for Clive Script Interface without profile context.

    Provides access to read-only operations that don't require a profile.
    For operations requiring a profile, use UnlockedCliveSi instead.

    Example:
        async with CliveSi() as clive:
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


class UnlockedCliveSi:
    """
    Clive Script Interface with profile context.

    This class provides full access to Clive functionality including operations
    that require an unlocked profile (transfers, authority updates, etc.).

    IMPORTANT: This class MUST be used as an async context manager (with 'async with' statement).
    The context manager ensures:
    - Profile is automatically loaded from the unlocked beekeeper wallet on entry (__aenter__)
    - Profile is automatically saved to storage on exit (__aexit__)
    - Proper cleanup of resources (node, wax interface, beekeeper)

    Use the factory function or context manager:
        async with clive_use_unlocked_profile() as clive:
            await clive.process.transfer(...).broadcast()

    Or directly:
        async with UnlockedCliveSi() as clive:
            await clive.process.transfer(...).broadcast()

    Note: Methods __aenter__ and __aexit__ delegate to setup() and close() respectively,
    following the same pattern as CLIWorld and TUIWorld.
    """

    def __init__(self) -> None:
        self._world = SIWorld()
        self._is_setup_called = False
        self.__show = ShowInterface(self)
        self.__process = ProfileOperationsInterface(self)
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
    def process(self) -> ProfileOperationsInterface:
        """Access to process operations. Requires context manager to be entered."""
        self._ensure_setup_called()
        return self.__process

    @property
    def configure(self) -> ConfigureInterface:
        """Access to configure operations. Requires context manager to be entered."""
        self._ensure_setup_called()
        return self.__configure

    async def setup(self) -> None:
        """Initialize the SI world and load profile. Called automatically by context manager."""
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
            raise SIContextManagerNotUsedError(
                "UnlockedCliveSi must be used as an async context manager. "
                "Use 'async with UnlockedCliveSi() as clive:' or 'async with clive_use_unlocked_profile() as clive:'"
            )
