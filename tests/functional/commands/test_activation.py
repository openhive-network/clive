from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.commands.unlock import Unlock, WalletDoesNotExistsError

if TYPE_CHECKING:
    import clive
    from clive.__private.core.profile import Profile
    from clive_local_tools.data.models import WalletInfo


async def test_unlock(
    world: clive.World,
    prepare_wallet_of_profile: WalletInfo,
    prepare_profile: Profile,  # noqa: ARG001
) -> None:
    # ARRANGE
    await world.beekeeper.api.lock_all()

    # ACT
    await world.commands.unlock(password=prepare_wallet_of_profile.password)

    # ASSERT
    assert world.app_state.is_unlocked


async def test_unlock_non_existing_wallet(
    world: clive.World,
    prepare_wallet_of_profile: WalletInfo,  # noqa: ARG001
    prepare_profile: Profile,  # noqa: ARG001
) -> None:
    # ACT & ASSERT
    with pytest.raises(WalletDoesNotExistsError), world.modified_connection_details(max_attempts=1):
        await Unlock(
            app_state=world.app_state,
            beekeeper=world.beekeeper,
            wallet="blabla",
            password="blabla",
        ).execute()


async def test_lock(
    world: clive.World,
    prepare_wallet_of_profile: WalletInfo,  # noqa: ARG001
    prepare_profile: Profile,  # noqa: ARG001
) -> None:
    # ARRANGE & ACT
    assert world.app_state.is_unlocked
    await world.commands.lock()

    # ASSERT
    assert not world.app_state.is_unlocked


async def test_unlock_again(
    world: clive.World,
    prepare_wallet_of_profile: WalletInfo,
    prepare_profile: Profile,  # noqa: ARG001
) -> None:
    # ARRANGE & ACT
    assert world.app_state.is_unlocked
    await world.commands.lock()
    await world.commands.unlock(password=prepare_wallet_of_profile.password)

    # ASSERT
    assert world.app_state.is_unlocked


async def test_lock_after_given_time(
    world: clive.World,
    prepare_wallet_of_profile: WalletInfo,
    prepare_profile: Profile,  # noqa: ARG001
) -> None:
    # ARRANGE
    time_to_sleep: Final[timedelta] = timedelta(seconds=2)
    await world.commands.lock()

    # ACT
    await world.commands.unlock(password=prepare_wallet_of_profile.password, time=time_to_sleep)
    assert world.app_state.is_unlocked
    await asyncio.sleep(time_to_sleep.total_seconds() + 1)  # extra second for notification

    # ASSERT
    assert not world.app_state.is_unlocked
