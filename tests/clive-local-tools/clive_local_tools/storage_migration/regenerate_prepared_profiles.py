"""
Will regenerate prepared profiles.

Profiles will be stored in current version of ProfileStorageModel.
If we are having storage in current version migration is not performed.
Use this script only if migration at some point is broken.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import test_tools as tt
from beekeepy import AsyncBeekeeper

from clive.__private.before_launch import _initialize_user_settings
from clive.__private.core.alarms.specific_alarms.recovery_account_warning_listed import (
    RecoveryAccountWarningListedAlarmIdentifier,
)
from clive.__private.core.commands.create_encryption_wallet import CreateEncryptionWallet
from clive.__private.core.commands.create_user_wallet import CreateUserWallet
from clive.__private.core.constants.setting_identifiers import DATA_PATH
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.formatters.case import underscore
from clive.__private.core.wallet_container import WalletContainer
from clive.__private.models.schemas import TransferOperation, convert_to_representation
from clive.__private.settings import safe_settings, settings
from clive.__private.storage.migrations import v0
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    ALT_WORKING_ACCOUNT1_PASSWORD,
)
from clive_local_tools.testnet_block_log.constants import ALT_WORKING_ACCOUNT1_DATA, ALT_WORKING_ACCOUNT2_DATA

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def _clear_previously_generated_profiles(path: Path) -> None:
    extensions = {".profile", ".wallet"}
    for item in path.rglob("*"):
        if item.suffix in extensions:
            item.unlink()


def _prepare_data_path(path: Path) -> None:
    settings.set(DATA_PATH, path)
    _initialize_user_settings()


def prepare_env(path: Path) -> None:
    _clear_previously_generated_profiles(path)
    _prepare_data_path(path)


@asynccontextmanager
async def prepare_encryption_service() -> AsyncGenerator[EncryptionService]:
    account_name = ALT_WORKING_ACCOUNT1_DATA.account.name
    password = ALT_WORKING_ACCOUNT1_PASSWORD
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory()) as beekeeper_cm:
        session = await beekeeper_cm.session
        user_wallet = await CreateUserWallet(
            session=session, profile_name=account_name, password=password
        ).execute_with_result()
        encryption_wallet = await CreateEncryptionWallet(
            session=session, profile_name=account_name, password=password
        ).execute_with_result()
        encryption_service = EncryptionService(WalletContainer(user_wallet, encryption_wallet))
        yield encryption_service


def create_model_from_scratch() -> v0.ProfileStorageModel:
    account_name = ALT_WORKING_ACCOUNT1_DATA.account.name
    return v0.ProfileStorageModel(
        name=account_name,
        working_account=account_name,
        tracked_accounts=[v0.StorageDefinitions.TrackedAccountStorageModel(name=account_name, alarms=[])],
        known_accounts=[account_name, ALT_WORKING_ACCOUNT2_DATA.account.name],
        key_aliases=[
            v0.StorageDefinitions.KeyAliasStorageModel(
                alias=ALT_WORKING_ACCOUNT1_KEY_ALIAS,
                public_key=ALT_WORKING_ACCOUNT1_DATA.account.public_key,
            )
        ],
        transaction=None,
        chain_id=None,
        node_address="https://api.hive.blog",
        should_enable_known_accounts=False,
    )


def save_encrypted_profile(encrypted: str) -> None:
    profile_directory = PersistentStorageService.get_profile_directory(ALT_WORKING_ACCOUNT1_DATA.account.name)
    filepath = profile_directory / f"v0{PersistentStorageService.PROFILE_FILENAME_SUFFIX}"
    filepath.write_text(encrypted)


async def _main() -> None:
    directory = Path(__file__).parent.absolute()

    prepare_env(directory / "without_alarms_and_operations")
    async with prepare_encryption_service() as encryption_service:
        profile_model = create_model_from_scratch()
        encrypted = await encryption_service.encrypt(profile_model.json(indent=4))
        save_encrypted_profile(encrypted)

    prepare_env(directory / "with_alarms")
    async with prepare_encryption_service() as encryption_service:
        profile_model = create_model_from_scratch()
        profile_model.tracked_accounts[0].alarms = [
            v0.StorageDefinitions.AlarmStorageModel(
                name=underscore("RecoveryAccountWarningListed"),
                is_harmless=False,
                identifier=RecoveryAccountWarningListedAlarmIdentifier(
                    recovery_account=ALT_WORKING_ACCOUNT2_DATA.account.name
                ),
            )
        ]
        encrypted = await encryption_service.encrypt(profile_model.json(indent=4))
        save_encrypted_profile(encrypted)

    prepare_env(directory / "with_operations")
    async with prepare_encryption_service() as encryption_service:
        profile_model = create_model_from_scratch()
        operation = TransferOperation(
            from_=ALT_WORKING_ACCOUNT1_DATA.account.name,
            to=ALT_WORKING_ACCOUNT2_DATA.account.name,
            amount=tt.Asset.Hive(1),
            memo="",
        )
        profile_model.transaction = v0.StorageDefinitions.TransactionStorageModel(
            transaction_core=v0.StorageDefinitions.TransactionCoreStorageModel(
                operations=[convert_to_representation(operation)]
            ),
            transaction_file_path=Path("example/path"),
        )
        encrypted = await encryption_service.encrypt(profile_model.json(indent=4))
        save_encrypted_profile(encrypted)


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
