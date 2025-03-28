from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from beekeepy import AsyncBeekeeper

from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer
from clive.__private.settings import safe_settings
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.storage_migration.helpers import (
    copy_profile_with_alarms,
    copy_profile_with_operations,
    copy_profile_without_alarms_and_operations,
)
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_NAME


@asynccontextmanager
async def prepare_persistent_storage_service() -> AsyncGenerator[PersistentStorageService, None]:
    profile_name = WORKING_ACCOUNT_NAME
    password = WORKING_ACCOUNT_NAME * 2
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory()) as beekeeper:
        session = await beekeeper.session
        wallet = await session.open_wallet(name=profile_name)
        unlocked_wallet = await wallet.unlock(password=password)
        encryption_wallet = await session.open_wallet(name=EncryptionService.get_encryption_wallet_name(profile_name))
        unlocked_encryption_wallet = await encryption_wallet.unlock(password=password)
        wallets = WalletContainer(unlocked_wallet, unlocked_encryption_wallet)
        encryption_service = EncryptionService(wallets)
        yield PersistentStorageService(encryption_service)


async def test_migrate_profile_without_alarms_and_operations() -> None:
    # ARRANGE
    copy_profile_without_alarms_and_operations(safe_settings.data_path)
    async with prepare_persistent_storage_service() as service:
        # ACT
        profile = await service.load_profile(WORKING_ACCOUNT_NAME)

        # ASSERT
        assert profile.name == WORKING_ACCOUNT_NAME, f"Profile with name {WORKING_ACCOUNT_NAME} should be loaded"


async def test_migrate_profile_with_alarms() -> None:
    # ARRANGE
    copy_profile_with_alarms(safe_settings.data_path)
    async with prepare_persistent_storage_service() as service:
        # ACT
        profile = await service.load_profile(WORKING_ACCOUNT_NAME)

        # ASSERT
        assert profile.name == WORKING_ACCOUNT_NAME, f"Profile with name {WORKING_ACCOUNT_NAME} should be loaded"

        alarms = profile.accounts.working._alarms
        assert alarms.all_alarms != [], "Alarms should be loaded from older profile version"


async def test_migrate_profile_with_operations() -> None:
    # ARRANGE
    copy_profile_with_operations(safe_settings.data_path)
    async with prepare_persistent_storage_service() as service:
        # ACT
        profile = await service.load_profile(WORKING_ACCOUNT_NAME)

        # ASSERT
        assert profile.name == WORKING_ACCOUNT_NAME, f"Profile with name {WORKING_ACCOUNT_NAME} should be loaded"

        assert profile.operations != [], "Operations should be loaded from older profile version"
