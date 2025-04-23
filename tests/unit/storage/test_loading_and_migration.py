from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from beekeepy import AsyncBeekeeper

from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer
from clive.__private.settings import safe_settings
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_PASSWORD
from clive_local_tools.storage_migration.helpers import (
    copy_profile_with_alarms,
    copy_profile_with_operations,
    copy_profile_without_alarms_and_operations,
)
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_NAME

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def prepare_persistent_storage_service(profile_name: str) -> AsyncGenerator[PersistentStorageService, None]:
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory()) as beekeeper:
        session = await beekeeper.session
        wallet = await session.open_wallet(name=profile_name)
        unlocked_wallet = await wallet.unlock(password=ALT_WORKING_ACCOUNT1_PASSWORD)
        encryption_wallet = await session.open_wallet(name=EncryptionService.get_encryption_wallet_name(profile_name))
        unlocked_encryption_wallet = await encryption_wallet.unlock(password=ALT_WORKING_ACCOUNT1_PASSWORD)
        wallets = WalletContainer(unlocked_wallet, unlocked_encryption_wallet)
        encryption_service = EncryptionService(wallets)
        yield PersistentStorageService(encryption_service)


async def test_migrate_profile_without_alarms_and_operations() -> None:
    # ARRANGE
    profile_name = ALT_WORKING_ACCOUNT1_NAME
    copy_profile_without_alarms_and_operations(safe_settings.data_path)
    async with prepare_persistent_storage_service(profile_name) as service:
        # ACT
        profile = await service.load_profile(profile_name)

        # ASSERT
        assert profile.name == profile_name, f"Profile with name {profile_name} should be loaded"


async def test_migrate_profile_with_alarms() -> None:
    # ARRANGE
    profile_name = ALT_WORKING_ACCOUNT1_NAME
    copy_profile_with_alarms(safe_settings.data_path)
    async with prepare_persistent_storage_service(profile_name) as service:
        # ACT
        profile = await service.load_profile(profile_name)

        # ASSERT
        assert profile.name == profile_name, f"Profile with name {profile_name} should be loaded"

        alarms = profile.accounts.working._alarms
        assert alarms.all_alarms != [], "Alarms should be loaded from older profile version"


async def test_migrate_profile_with_operations() -> None:
    # ARRANGE
    profile_name = ALT_WORKING_ACCOUNT1_NAME
    copy_profile_with_operations(safe_settings.data_path)
    async with prepare_persistent_storage_service(profile_name) as service:
        # ACT
        profile = await service.load_profile(profile_name)

        # ASSERT
        assert profile.name == profile_name, f"Profile with name {profile_name} should be loaded"

        assert profile.operations != [], "Operations should be loaded from older profile version"
