from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    import clive
    from tests import WalletInfo


def test_activate(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE
    world.beekeeper.api.lock_all()

    # ACT
    world.commands.activate(password=wallet.password)

    # ASSERT
    assert world.app_state.is_active()


def test_deactivate(world: clive.World, wallet: WalletInfo) -> None:  # noqa: ARG001
    # ARRANGE & ACT
    assert world.app_state.is_active()
    world.commands.deactivate()

    # ASSERT
    assert not world.app_state.is_active()


def test_reactivate(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    assert world.app_state.is_active()
    world.commands.deactivate()
    world.commands.activate(password=wallet.password)

    # ASSERT
    assert world.app_state.is_active()


def test_deactivate_after_given_time(world: clive.World, wallet: WalletInfo) -> None:  # noqa: ARG001
    time_to_sleep: Final[int] = 2

    # ARRANGE
    assert world.app_state.is_active()
    world.beekeeper.api.set_timeout(seconds=time_to_sleep)
    assert world.app_state.is_active()

    # ACT
    sleep(time_to_sleep + 1)

    # ASSERT
    assert not world.app_state.is_active()
