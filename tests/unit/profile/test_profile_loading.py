from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from beekeepy import AsyncBeekeeper

from clive.__private.core.commands.create_profile_wallets import CreateProfileWallets
from clive.__private.core.commands.get_unlocked_user_wallet import GetUnlockedUserWallet
from clive.__private.core.commands.save_profile import SaveProfile
from clive.__private.core.profile import Profile
from clive.__private.core.world import CLIWorld, World
from clive.__private.settings import safe_settings

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@pytest.fixture
async def beekeeper() -> AsyncIterator[AsyncBeekeeper]:
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory()) as beekeeper_cm:
        yield beekeeper_cm


async def create_profile_and_wallet(beekeeper: AsyncBeekeeper, profile_name: str, *, lock: bool = False) -> None:
    result = await CreateProfileWallets(
        session=await beekeeper.session, profile_name=profile_name, password=profile_name
    ).execute_with_result()
    profile = Profile.create(profile_name)
    await SaveProfile(
        profile=profile,
        unlocked_wallet=result.unlocked_user_wallet,
        unlocked_encryption_wallet=result.unlocked_encryption_wallet,
    ).execute()
    if lock:
        await result.unlocked_user_wallet.lock()
        await result.unlocked_encryption_wallet.lock()


def test_if_profile_is_loaded(world: World, prepare_profile_with_wallet: None, wallet_name: str) -> None:  # noqa: ARG001
    # ARRANGE, ACT & ASSERT
    assert world.profile.name == wallet_name, f"Profile {wallet_name} should be loaded"


async def test_if_unlocked_profile_is_loaded_other_was_saved(beekeeper: AsyncBeekeeper) -> None:
    # ARRANGE
    additional_profile_name = "first"
    unlocked_profile_name = "second"
    additional_profile_name2 = "third"
    await create_profile_and_wallet(beekeeper, additional_profile_name, lock=True)
    await create_profile_and_wallet(beekeeper, additional_profile_name2, lock=True)

    # This profile should be unlocked
    await create_profile_and_wallet(beekeeper, unlocked_profile_name)

    # ACT
    # Check if the unlocked profile is loaded
    token = await (await beekeeper.session).token

    cli_world = CLIWorld()
    cli_world.beekeeper_manager.settings.http_endpoint = beekeeper.http_endpoint
    cli_world.beekeeper_manager.settings.use_existing_session = token

    async with cli_world as world_cm:
        loaded_profile_name = world_cm.profile.name

    # ASSERT
    assert loaded_profile_name == unlocked_profile_name, (
        f"Unlocked profile is {unlocked_profile_name} but loaded is {loaded_profile_name}"
    )
    actual_unlocked_profile = await GetUnlockedUserWallet(session=await beekeeper.session).execute_with_result()
    assert actual_unlocked_profile.name == unlocked_profile_name
    assert Profile.list_profiles() == sorted([additional_profile_name, unlocked_profile_name, additional_profile_name2])


async def test_loading_profile_without_beekeeper_session() -> None:
    # ACT
    world = World()
    await world.setup()

    # ASSERT
    assert world._profile is None, "Without beekeeper session profile should be not loaded"


async def test_loading_profile_without_beekeeper_session_cli() -> None:
    # ACT
    world = CLIWorld()
    await CLIWorld().setup()

    # ASSERT
    assert world._profile is None, "CLIWorld should be loaded and profile should be set to None"
    assert world.beekeeper_manager._wallets is None, "CLIWorld should be loaded and wallets should be not available"
    assert world._wax_interface is None, "CLIWorld should be loaded but wax interface should be not loaded yet"
    assert world._node is None, "CLIWorld should be loaded and node should be set to None"
