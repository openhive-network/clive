from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Final

import pytest
from beekeepy._interface.exceptions import NoWalletWithSuchNameError

from clive.__private.core.commands.activate import Activate

if TYPE_CHECKING:
    import clive
    from clive_local_tools.data.models import WalletInfo


async def test_activate(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE
    await world.session.lock_all()

    # ACT
    await world.commands.activate(password=wallet.password)

    # ASSERT
    assert world.app_state.is_active


async def test_activate_non_existing_wallet(world: clive.World) -> None:
    # ACT & ASSERT
    with pytest.raises(NoWalletWithSuchNameError):
        await Activate(app_state=world.app_state, session=world.session, wallet="blabla", password="blabla").execute()


async def test_deactivate(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    assert world.app_state.is_active
    await world.commands.deactivate()

    # ASSERT
    assert not world.app_state.is_active


async def test_reactivate(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    assert world.app_state.is_active
    await world.commands.deactivate()
    await world.commands.activate(password=wallet.password)

    # ASSERT
    assert world.app_state.is_active


async def test_deactivate_after_given_time(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE
    time_to_sleep: Final[timedelta] = timedelta(seconds=2)
    await world.commands.deactivate()

    # ACT
    await world.commands.activate(password=wallet.password, time=time_to_sleep)
    assert world.app_state.is_active
    await asyncio.sleep(time_to_sleep.total_seconds() + 2)  # extra second for notification

    # ASSERT
    assert not world.app_state.is_active
