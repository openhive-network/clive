from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from beekeepy import AsyncBeekeeper

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.get_unlocked_wallet import GetUnlockedWallet
from clive.__private.core.constants.tui.profile import WELCOME_PROFILE_NAME
from clive.__private.core.profile import Profile
from clive.__private.core.world import CLIWorld, TUIWorld, World
from clive.__private.settings import safe_settings

if TYPE_CHECKING:
    from typing import AsyncIterator

    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
async def beekeeper_for_remote_use() -> AsyncIterator[AsyncBeekeeper]:
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_factory()) as beekeeper_cm:
        yield beekeeper_cm


async def create_profile_and_wallet(beekeeper: AsyncBeekeeper, profile_name: str, *, lock: bool = False) -> None:
    Profile.create(profile_name).save()
    result = await CreateWallet(
        session=await beekeeper.session, wallet_name=profile_name, password=profile_name
    ).execute_with_result()
    if lock:
        await result.unlocked_wallet.lock()


def test_if_profile_is_loaded(world: World, prepare_profile_with_wallet: None, wallet_name: str) -> None:  # noqa: ARG001
    # ARRANGE, ACT & ASSERT
    assert world.profile.name == wallet_name, f"Profile {wallet_name} should be loaded"


async def test_if_unlocked_profile_is_loaded_other_was_saved(
    beekeeper_for_remote_use: AsyncBeekeeper, beekeeper_session_token_env_context_factory: EnvContextFactory
) -> None:
    # ARRANGE
    additional_profile_name = "first"
    unlocked_profile_name = "second"
    additional_profile_name2 = "third"
    await create_profile_and_wallet(beekeeper_for_remote_use, additional_profile_name, lock=True)
    await create_profile_and_wallet(beekeeper_for_remote_use, additional_profile_name2, lock=True)

    # This profile should be unlocked
    await create_profile_and_wallet(beekeeper_for_remote_use, unlocked_profile_name)

    # ACT
    # Check if the unlocked profile is loaded
    with beekeeper_session_token_env_context_factory(await (await beekeeper_for_remote_use.session).token):
        async with CLIWorld(beekeepy_settings_or_url=beekeeper_for_remote_use.settings) as world_cm:
            loaded_profile_name = world_cm.profile.name

    # ASSERT
    assert (
        loaded_profile_name == unlocked_profile_name
    ), f"Unlocked profile is {unlocked_profile_name} but loaded is {loaded_profile_name}"
    actual_unlocked_profile = await GetUnlockedWallet(
        session=await beekeeper_for_remote_use.session
    ).execute_with_result()
    assert actual_unlocked_profile.name == unlocked_profile_name
    assert Profile.list_profiles() == sorted([additional_profile_name, unlocked_profile_name, additional_profile_name2])


async def test_loading_profile_without_beekeeper_session() -> None:
    # ACT
    world = World()
    await world.setup()

    # ASSERT
    assert world._profile is None, "Without beekeeper session profile should be not loaded"


async def test_loading_profile_without_beekeeper_session_tui() -> None:
    # ACT
    world = TUIWorld()
    await world.setup()

    # ASSERT
    assert world.profile is not None, "Without beekeeper session welcome profile should be created"
    assert (
        world.profile.name == WELCOME_PROFILE_NAME
    ), f"Without beekeeper session profile name should be {WELCOME_PROFILE_NAME}"


async def test_loading_profile_without_beekeeper_session_cli() -> None:
    # ACT & ASSERT
    with pytest.raises(CLINoProfileUnlockedError):
        await CLIWorld().setup()
