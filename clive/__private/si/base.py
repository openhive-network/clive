from __future__ import annotations

from typing import TYPE_CHECKING, Self

from clive.__private.before_launch import prepare_before_launch
from clive.__private.core.world import World
from clive.__private.si.configure import ConfigureInterface
from clive.__private.si.core.configure import ProfileLoad
from clive.__private.si.generate import GenerateInterface
from clive.__private.si.process import ProfileOperationsInterface
from clive.__private.si.show import ShowInterface, ShowInterfaceNoProfile

if TYPE_CHECKING:
    from types import TracebackType


def clive_use_unlocked_profile() -> UnlockedCliveSi:
    """
    Factory function to create a Clive SI instance with an unlocked profile.

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
        clive = CliveSi()
        witnesses = await clive.show.witnesses("bob")
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

    Use the factory function or context manager:
        async with clive_use_unlocked_profile() as clive:
            await clive.process.transfer(...).broadcast()

    Or directly:
        async with UnlockedCliveSi() as clive:
            await clive.process.transfer(...).broadcast()
    """

    def __init__(self) -> None:
        self._world = World()
        self.show = ShowInterface(self)
        self.process = ProfileOperationsInterface(self)
        self.configure = ConfigureInterface(self)
        self.generate = GenerateInterface()
        self.__prepare_before_launch()

    async def __aenter__(self) -> Self:
        await self.setup()
        await ProfileLoad(self._world).run()
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.close()

    def __prepare_before_launch(self) -> None:
        prepare_before_launch()

    async def setup(self) -> None:
        await self._world.setup()

    async def close(self) -> None:
        await self._world.close()
