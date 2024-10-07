from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.commands.unlock import Unlock, WalletDoesNotExistsError

if TYPE_CHECKING:
    import clive
    from clive_local_tools.data.models import WalletInfo


async def test_unlock(world: clive.World, prepare_beekeeper_wallet_with_session: WalletInfo) -> None:
    # ARRANGE
    await world.commands.lock_all()

    # ACT
    await world.commands.unlock(password=prepare_beekeeper_wallet_with_session.password)

    # ASSERT
    assert world.app_state.is_unlocked


async def test_unlock_non_existing_wallet(world: clive.World) -> None:
    # ACT & ASSERT
    with pytest.raises(WalletDoesNotExistsError), world.modified_connection_details(max_attempts=1):
        await Unlock(
            app_state=world.app_state,
            beekeeper=world.beekeeper,
            wallet="blabla",
            password="blabla",
        ).execute()


async def test_lock(world: clive.World) -> None:
    # ARRANGE & ACT
    assert world.app_state.is_unlocked
    await world.commands.lock()

    # ASSERT
    assert not world.app_state.is_unlocked


async def test_unlock_again(world: clive.World, prepare_beekeeper_wallet_with_session: WalletInfo) -> None:
    # ARRANGE & ACT
    assert world.app_state.is_unlocked
    await world.commands.lock()
    await world.commands.unlock(password=prepare_beekeeper_wallet_with_session.password)

    # ASSERT
    assert world.app_state.is_unlocked


async def test_lock_after_given_time(world: clive.World, prepare_beekeeper_wallet_with_session: WalletInfo) -> None:
    # ARRANGE
    time_to_sleep: Final[timedelta] = timedelta(seconds=2)
    await world.commands.lock()

    # ACT
    await world.commands.unlock(password=prepare_beekeeper_wallet_with_session.password, time=time_to_sleep)
    assert world.app_state.is_unlocked
    await asyncio.sleep(time_to_sleep.total_seconds() + 1)  # extra second for notification
    # app_state doesn't get auto locked when there is no notification server
    await world.commands.sync_state_with_beekeeper()

    # ASSERT
    assert not world.app_state.is_unlocked
