from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Final, Literal

import pytest

from clive.__private.core.commands.is_wallet_unlocked import IsWalletUnlocked
from clive.__private.core.commands.recover_wallets import CannotRecoverWalletsError
from clive.__private.core.commands.unlock import Unlock
from clive.__private.core.encryption import EncryptionService

if TYPE_CHECKING:
    from beekeepy.asynchronous import AsyncBeekeeper

    from clive.__private.core.profile import Profile
    from clive.__private.core.world import World


async def test_unlock(
    world: World,
    prepare_profile_with_wallet: Profile,  # noqa: ARG001
    wallet_password: str,
) -> None:
    # ARRANGE
    await world.beekeeper_manager.session.lock_all()

    # ACT
    await world.commands.unlock(password=wallet_password)

    # ASSERT
    assert world.app_state.is_unlocked


async def test_unlock_non_existing_wallets(world: World, prepare_profile_with_wallet: Profile) -> None:  # noqa: ARG001
    # ACT & ASSERT
    with pytest.raises(CannotRecoverWalletsError):
        await Unlock(
            app_state=world.app_state,
            session=world.beekeeper_manager.session,
            profile_name="blabla",
            password="blabla",
        ).execute()


@pytest.mark.parametrize("wallet_type", ["user_wallet", "encryption_wallet"])
async def test_unlock_recovers_missing_wallet(
    world: World,
    prepare_profile_with_wallet: Profile,
    beekeeper: AsyncBeekeeper,
    wallet_password: str,
    wallet_type: Literal["user_wallet", "encryption_wallet"],
) -> None:
    # ARRANGE
    profile = prepare_profile_with_wallet

    encryption_wallet = (await world.commands.get_unlocked_encryption_wallet()).result_or_raise
    encryption_keys_before = await encryption_wallet.public_keys

    beekeeper_working_directory = beekeeper.settings.working_directory
    assert beekeeper_working_directory is not None, "Beekeeper working directory should be set"

    wallet_filenames = {
        "user_wallet": f"{profile.name}.wallet",
        "encryption_wallet": f"{EncryptionService.get_encryption_wallet_name(profile.name)}.wallet",
    }

    wallet_filename = wallet_filenames[wallet_type]

    wallet_filepath = beekeeper_working_directory / wallet_filename
    assert wallet_filepath.is_file(), "Wallet file should exist"

    # remove wallet
    wallet_filepath.unlink()
    assert not wallet_filepath.exists(), "Wallet file should not exist"

    # restart beekeeper so wallets are loaded again because beekeeper is caching them
    # and recovery process is not triggered
    await world.close()
    await world.setup()

    # ACT
    # unlock takes place during load_profile
    await world.load_profile(profile.name, wallet_password)

    # ASSERT
    assert world.app_state.is_unlocked, "Wallet should be unlocked"
    assert wallet_filepath.is_file(), "Wallet file should be recovered"

    if wallet_type == "user_wallet":
        user_wallet = (await world.commands.get_unlocked_user_wallet()).result_or_raise
        public_keys = await user_wallet.public_keys
        assert public_keys == [], "User wallet should be recovered with no keys"
    else:
        encryption_wallet = (await world.commands.get_unlocked_encryption_wallet()).result_or_raise
        public_keys = await encryption_wallet.public_keys
        assert public_keys == encryption_keys_before, "Encryption wallet should be recovered with the same keys"


async def test_lock(world: World, prepare_profile_with_wallet: Profile) -> None:  # noqa: ARG001
    # ARRANGE & ACT
    assert world.app_state.is_unlocked
    await world.commands.lock()
    world.profile.skip_saving()  # cannot save profile when it is locked because encryption is not possible

    # ASSERT
    assert not world.app_state.is_unlocked


async def test_unlock_again(
    world: World,
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
    world: World,
    prepare_profile_with_wallet: Profile,  # noqa: ARG001
    wallet_password: str,
) -> None:
    # ARRANGE
    time_to_sleep: Final[timedelta] = timedelta(seconds=2)
    await world.commands.lock()
    world.profile.skip_saving()  # cannot save profile when it is locked because encryption is not possible

    # ACT
    await world.commands.unlock(password=wallet_password, time=time_to_sleep, permanent=False)
    assert world.app_state.is_unlocked
    await asyncio.sleep(time_to_sleep.total_seconds() + 1)  # extra second for notification

    # ASSERT
    is_wallet_unlocked_in_beekeeper = await IsWalletUnlocked(
        wallet=world.beekeeper_manager.user_wallet
    ).execute_with_result()
    assert not is_wallet_unlocked_in_beekeeper, "Wallet should be locked in beekeeper"

    await world.commands.sync_state_with_beekeeper()

    assert not world.app_state.is_unlocked, "Wallet should be locked in clive"
