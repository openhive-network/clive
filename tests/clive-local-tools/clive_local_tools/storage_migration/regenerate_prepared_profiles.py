"""
Will regenerate prepared profiles.

We explicitly specify version of the profile to be generated, then in tests we apply
all migrations to the profile and check if it is loaded correctly.
If migration at some point is broken, we can regenerate storage files and keep tests.
"""

from __future__ import annotations

import asyncio
import shutil
import tempfile
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Final

import test_tools as tt
from beekeepy import AsyncBeekeeper

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
from clive.__private.storage.migrations.v0 import ProfileStorageModel
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    ALT_WORKING_ACCOUNT1_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    ALT_WORKING_ACCOUNT2_DATA,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from clive_local_tools.data.models import AccountData


ACCOUNT_DATA: Final[AccountData] = ALT_WORKING_ACCOUNT1_DATA
PROFILE_NAME: Final[str] = ALT_WORKING_ACCOUNT1_NAME
PROFILE_PASSWORD: Final[str] = ALT_WORKING_ACCOUNT1_PASSWORD
VERSION: Final[int] = ProfileStorageModel.get_this_version()
OPERATION: Final[TransferOperation] = TransferOperation(
    from_=ACCOUNT_DATA.account.name,
    to=ALT_WORKING_ACCOUNT2_DATA.account.name,
    amount=tt.Asset.Hive(1),
    memo="",
)


@asynccontextmanager
async def prepare_encryption_service() -> AsyncGenerator[EncryptionService]:
    account_name = PROFILE_NAME
    password = PROFILE_PASSWORD
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


def create_model_from_scratch() -> ProfileStorageModel:
    account_name = PROFILE_NAME
    return ProfileStorageModel(
        name=account_name,
        working_account=account_name,
        tracked_accounts=[ProfileStorageModel._TrackedAccountStorageModel(name=account_name, alarms=[])],
        known_accounts=[account_name, ALT_WORKING_ACCOUNT2_DATA.account.name],
        key_aliases=[
            ProfileStorageModel._KeyAliasStorageModel(
                alias=ALT_WORKING_ACCOUNT1_KEY_ALIAS,
                public_key=ACCOUNT_DATA.account.public_key,
            )
        ],
        transaction=None,
        chain_id=None,
        node_address="https://api.hive.blog",
        should_enable_known_accounts=False,
    )


def save_encrypted_profile(encrypted: str) -> None:
    profile_directory = PersistentStorageService.get_profile_directory(PROFILE_NAME)
    profile_directory.mkdir(parents=True)
    filepath = profile_directory / PersistentStorageService.get_version_profile_filename(VERSION)
    filepath.write_text(encrypted)


@contextmanager
def copy_profile_files_from_tmp_dir(dst_dir_name: str) -> Generator[None, None]:
    dst_dir = Path(__file__).parent.absolute() / dst_dir_name

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        settings.set(DATA_PATH, tmp_dir_name)
        yield

        for path in Path(tmp_dir_name).rglob("*"):
            if path.suffix in {".wallet", ".profile"}:
                dst_path = dst_dir / path.relative_to(tmp_dir_name)
                shutil.copy(path, dst_path)


async def _main() -> None:
    with copy_profile_files_from_tmp_dir("without_alarms_and_operations"):
        async with prepare_encryption_service() as encryption_service:
            profile_model = create_model_from_scratch()
            encrypted = await encryption_service.encrypt(profile_model.json(indent=4))
            save_encrypted_profile(encrypted)

    with copy_profile_files_from_tmp_dir("with_alarms"):
        async with prepare_encryption_service() as encryption_service:
            profile_model = create_model_from_scratch()
            profile_model.tracked_accounts[0].alarms = [
                ProfileStorageModel._AlarmStorageModel(
                    name=underscore("RecoveryAccountWarningListed"),
                    is_harmless=False,
                    identifier=RecoveryAccountWarningListedAlarmIdentifier(
                        recovery_account=ALT_WORKING_ACCOUNT2_DATA.account.name
                    ),
                )
            ]
            encrypted = await encryption_service.encrypt(profile_model.json(indent=4))
            save_encrypted_profile(encrypted)

    with copy_profile_files_from_tmp_dir("with_operations"):
        async with prepare_encryption_service() as encryption_service:
            profile_model = create_model_from_scratch()
            profile_model.transaction = ProfileStorageModel._TransactionStorageModel(
                transaction_core=ProfileStorageModel._TransactionCoreStorageModel(
                    operations=[convert_to_representation(OPERATION)]
                ),
                transaction_file_path=Path("example/path"),
            )
            encrypted = await encryption_service.encrypt(profile_model.json(indent=4))
            save_encrypted_profile(encrypted)


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
