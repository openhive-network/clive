from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.encryption import EncryptionService

if TYPE_CHECKING:
    from beekeepy import AsyncBeekeeper

    from clive.__private.core.profile import Profile
    from clive.__private.core.world import World


async def test_beekeeper_recovers_from_stale_state(
    world: World,
    prepare_profile_with_wallet: Profile,
    beekeeper: AsyncBeekeeper,
    wallet_password: str,
) -> None:
    """Verify that beekeeper recovers when stale files in working directory prevent startup."""
    profile = prepare_profile_with_wallet

    beekeeper_working_directory = beekeeper.settings.working_directory
    assert beekeeper_working_directory is not None, "Beekeeper working directory should be set"

    user_wallet_path = beekeeper_working_directory / f"{profile.name}.wallet"
    encryption_wallet_name = EncryptionService.get_encryption_wallet_name(profile.name)
    encryption_wallet_path = beekeeper_working_directory / f"{encryption_wallet_name}.wallet"

    assert user_wallet_path.is_file(), "User wallet file should exist"
    assert encryption_wallet_path.is_file(), "Encryption wallet file should exist"

    user_wallet_content = user_wallet_path.read_bytes()
    encryption_wallet_content = encryption_wallet_path.read_bytes()

    # Write an invalid config.ini to simulate stale state from a previous version
    stale_config = beekeeper_working_directory / "config.ini"
    stale_config.write_text("[invalid]\ngarbage=that_will_crash_beekeeper\n")

    # Restart beekeeper — the stale config.ini should trigger recovery
    await world.close()
    await world.setup()

    # Verify beekeeper is running (accessing the property asserts it's not None internally)
    assert world.beekeeper_manager.beekeeper

    # Verify .wallet files were preserved
    assert user_wallet_path.is_file(), "User wallet file should be preserved after recovery"
    assert encryption_wallet_path.is_file(), "Encryption wallet file should be preserved after recovery"
    assert user_wallet_path.read_bytes() == user_wallet_content, "User wallet content should be unchanged"
    assert encryption_wallet_path.read_bytes() == encryption_wallet_content, (
        "Encryption wallet content should be unchanged"
    )

    # Verify we can still unlock and use the wallets
    await world.load_profile(profile.name, wallet_password)
    assert world.app_state.is_unlocked, "Should be able to unlock after recovery"
