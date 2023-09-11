from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.commands.activate import Activate, WalletDoesNotExistsError

if TYPE_CHECKING:
    import clive
    from tests import WalletInfo


async def test_activate(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE
    await world.beekeeper.api.lock_all()

    # ACT
    await world.commands.activate(password=wallet.password)

    # ASSERT
    assert await world.app_state.is_active


async def test_activate_non_existing_wallet(world: clive.World) -> None:
    # ACT & ASSERT
    with pytest.raises(WalletDoesNotExistsError), world.modified_connection_details(max_attempts=1):
        await Activate(
            app_state=world.app_state, beekeeper=world.beekeeper, wallet="blabla", password="blabla"
        ).execute()


async def test_deactivate(world: clive.World, wallet: WalletInfo) -> None:  # noqa: ARG001
    # ARRANGE & ACT
    assert await world.app_state.is_active
    await world.commands.deactivate()

    # ASSERT
    assert not await world.app_state.is_active


async def test_reactivate(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    assert await world.app_state.is_active
    await world.commands.deactivate()
    await world.commands.activate(password=wallet.password)

    # ASSERT
    assert await world.app_state.is_active


async def test_deactivate_after_given_time(world: clive.World, wallet: WalletInfo) -> None:
    # ARRANGE
    time_to_sleep: Final[timedelta] = timedelta(seconds=2)
    await world.commands.deactivate()

    # ACT
    await world.commands.activate(password=wallet.password, time=time_to_sleep)
    assert await world.app_state.is_active
    await asyncio.sleep(time_to_sleep.total_seconds() + 1)  # extra second for notification

    # ASSERT
    assert not await world.app_state.is_active
