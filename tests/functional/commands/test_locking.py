from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Final

import pytest
from beekeepy.exceptions import NoWalletWithSuchNameError

from clive.__private.core.commands.unlock import Unlock

if TYPE_CHECKING:
    import clive
    from clive.__private.core.profile import Profile


async def test_unlock(
    world: clive.World,
    prepare_profile_with_wallet: Profile,  # noqa: ARG001
    wallet_password: str,
) -> None:
    # ARRANGE
    await world._session_ensure.lock_all()

    # ACT
    await world.commands.unlock(password=wallet_password)

    # ASSERT
    assert world.app_state.is_unlocked


async def test_unlock_non_existing_wallet(world: clive.World, prepare_profile_with_wallet: Profile) -> None:  # noqa: ARG001
    # ACT & ASSERT
    with pytest.raises(NoWalletWithSuchNameError):
        await Unlock(
            app_state=world.app_state,
            session=world._session_ensure,
            wallet_name="blabla",
            password="blabla",
        ).execute()


async def test_lock(world: clive.World, prepare_profile_with_wallet: Profile) -> None:  # noqa: ARG001
    # ARRANGE & ACT
    assert world.app_state.is_unlocked
    await world.commands.lock()

    # ASSERT
    assert not world.app_state.is_unlocked


async def test_unlock_again(
    world: clive.World,
    prepare_profile_with_wallet: Profile,  # noqa: ARG001
    wallet_password: str,
) -> None:
    # ARRANGE & ACT
    assert world.app_state.is_unlocked
    await world.commands.lock()
    await world.commands.unlock(password=wallet_password)

    # ASSERT
    assert world.app_state.is_unlocked


async def test_lock_after_given_time(
    world: clive.World,
    prepare_profile_with_wallet: Profile,  # noqa: ARG001
    wallet_password: str,
) -> None:
    # ARRANGE
    time_to_sleep: Final[timedelta] = timedelta(seconds=2)
    await world.commands.lock()

    # ACT
    await world.commands.unlock(password=wallet_password, time=time_to_sleep)
    assert world.app_state.is_unlocked
    await asyncio.sleep(time_to_sleep.total_seconds() + 1)  # extra second for notification

    # ASSERT
    assert not world.app_state.is_unlocked
