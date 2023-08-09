from __future__ import annotations

from datetime import timedelta
from time import sleep
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.commands.activate import Activate, WalletDoesNotExistsError

if TYPE_CHECKING:
    import clive
    from tests import WalletInfo


def test_activate(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE
    world.beekeeper.api.lock_all()

    # ACT
    world.commands.activate(password=wallet.password)

    # ASSERT
    assert world.app_state.is_active


def test_activate_non_existing_wallet(world: clive.World) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(WalletDoesNotExistsError):
        Activate(app_state=world.app_state, beekeeper=world.beekeeper, wallet="blabla", password="blabla").execute()


def test_deactivate(world: clive.World, wallet: WalletInfo) -> None:  # noqa: ARG001
    # ARRANGE & ACT
    assert world.app_state.is_active
    world.commands.deactivate()

    # ASSERT
    assert not world.app_state.is_active


def test_reactivate(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    assert world.app_state.is_active
    world.commands.deactivate()
    world.commands.activate(password=wallet.password)

    # ASSERT
    assert world.app_state.is_active


def test_deactivate_after_given_time(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE
    time_to_sleep: Final[timedelta] = timedelta(seconds=2.2)
    world.beekeeper.api.lock_all()

    # ACT
    world.commands.activate(password=wallet.password, time=time_to_sleep)
    assert world.app_state.is_active
    sleep(time_to_sleep.total_seconds())

    # ASSERT
    assert not world.app_state.is_active
