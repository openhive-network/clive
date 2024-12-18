from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.commands.create_profile_encryption_wallet import CreateProfileEncryptionWallet
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.core.world import World
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    ALT_WORKING_ACCOUNT1_PASSWORD,
    WORKING_ACCOUNT_KEY_ALIAS,
)
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
)

if TYPE_CHECKING:
    from typing import AsyncGenerator

    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive.__private.core.encryption import EncryptionService


@pytest.fixture
async def prepare_profile_without_working_account(
    prepare_profile: Profile, encryption_service: EncryptionService
) -> Profile:
    prepare_profile.accounts.unset_working_account()
    await prepare_profile.save(encryption_service)
    return prepare_profile


@pytest.fixture
async def alt_prepare_profile(beekeeper: Beekeeper, encryption_service: EncryptionService) -> Profile:
    profile = Profile.create(
        ALT_WORKING_ACCOUNT1_NAME,
        working_account=WorkingAccount(name=ALT_WORKING_ACCOUNT1_NAME),
        watched_accounts=[WatchedAccount(name) for name in WATCHED_ACCOUNTS_NAMES],
    )
    await CreateProfileEncryptionWallet(
        beekeeper=beekeeper, profile_name=WORKING_ACCOUNT_DATA.account.name, password=ALT_WORKING_ACCOUNT1_PASSWORD
    ).execute()
    await CreateWallet(
        beekeeper=beekeeper, wallet=WORKING_ACCOUNT_DATA.account.name, password=ALT_WORKING_ACCOUNT1_PASSWORD
    ).execute()
    await profile.save(encryption_service)
    return profile


@pytest.fixture
async def alt_world(alt_prepare_profile: Profile) -> World:
    return World(profile_name=alt_prepare_profile.name)  # we must point to alternative profile


@pytest.fixture
async def alt_prepare_beekeeper_wallet(alt_world: World) -> AsyncGenerator[World]:
    async with alt_world as alt_world_cm:
        alt_world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}"),
            PrivateKeyAliased(
                value=ALT_WORKING_ACCOUNT1_DATA.account.private_key, alias=f"{ALT_WORKING_ACCOUNT1_KEY_ALIAS}"
            ),
        )
        await alt_world_cm.commands.sync_data_with_beekeeper()
        await alt_world_cm.profile.save(alt_world.encryption_service)  # required for saving imported keys aliases
        yield alt_world_cm
