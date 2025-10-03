from __future__ import annotations

from typing import TYPE_CHECKING, Self

from clive.__private.before_launch import prepare_before_launch
from clive.__private.core.world import World
from clive.__private.si.configure import ConfigureInterface
from clive.__private.si.core.configure import ProfileLoad
from clive.__private.si.generate import GenerateInterface
from clive.__private.si.process import ProcessInterface
from clive.__private.si.show import ShowInterface, ShowInterfaceNoProfile

if TYPE_CHECKING:
    from types import TracebackType


def clive_use_unlocked_profile() -> Profile:
    """Get a Profile context with an unlocked profile."""
    return CliveSi().use_unlocked_profile()


class CliveSi:
    """
    Main entry point for SI interfaces without a profile context.

    Provides access to show and generate interfaces.
    """

    def __init__(self) -> None:
        self.show = ShowInterfaceNoProfile()
        self.generate = GenerateInterface()

    async def __aenter__(self) -> Self:
        return self

    def use_unlocked_profile(self) -> Profile:
        """Return a Profile context for an unlocked profile."""
        return Profile()

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        pass


class ProfileBase:
    """
    Base class for SI interfaces with a profile context.

    Provides access to world, show, process, configure, and generate interfaces.
    """

    def __init__(self) -> None:
        self.world = World()
        self.show = ShowInterface(self)
        self.process = ProcessInterface(self)
        self.configure = ConfigureInterface(self)
        self.generate = GenerateInterface()
        self.__prepare_before_launch()

    async def __aenter__(self) -> Self:
        await self.setup()
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.close()

    def __prepare_before_launch(self) -> None:
        prepare_before_launch()

    async def setup(self) -> None:
        await self.world.setup()

    async def close(self) -> None:
        await self.world.close()


class Profile(ProfileBase):
    """Profile context for an already unlocked profile."""

    async def __aenter__(self) -> Self:
        await super().__aenter__()
        await ProfileLoad(self.world).run()
        return self
