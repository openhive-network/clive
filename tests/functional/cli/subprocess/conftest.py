from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    ALT_WORKING_ACCOUNT1_PASSWORD,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from typing import AsyncGenerator

    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.world import World


@pytest.fixture
async def prepare_profile(beekeeper: Beekeeper) -> Profile:
    profile1 = Profile.create(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_NAME),
        watched_accounts=[WatchedAccount(name) for name in WATCHED_ACCOUNTS_NAMES],
    )
    await CreateWallet(beekeeper=beekeeper, wallet=WORKING_ACCOUNT_NAME, password=WORKING_ACCOUNT_PASSWORD).execute()
    profile1.save()
    await beekeeper.api.lock_all()
    profile2 = Profile.create(
        ALT_WORKING_ACCOUNT1_NAME,
        working_account=WorkingAccount(name=ALT_WORKING_ACCOUNT1_NAME),
        watched_accounts=[WatchedAccount(name) for name in WATCHED_ACCOUNTS_NAMES],
    )
    await CreateWallet(
        beekeeper=beekeeper, wallet=ALT_WORKING_ACCOUNT1_NAME, password=ALT_WORKING_ACCOUNT1_PASSWORD
    ).execute()
    profile2.save()
    return profile2


@pytest.fixture
async def prepare_beekeeper_wallet(world: World) -> AsyncGenerator[World]:
    async with world as world_cm:
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}"),
            PrivateKeyAliased(
                value=ALT_WORKING_ACCOUNT1_DATA.account.private_key, alias=f"{ALT_WORKING_ACCOUNT1_KEY_ALIAS}"
            ),
        )
        await world_cm.commands.sync_data_with_beekeeper()
        world_cm.profile.save()  # required for saving imported keys aliases
        yield world_cm


@pytest.fixture
async def prepare_profile_without_working_account(prepare_beekeeper_wallet: World) -> Profile:
    prepare_beekeeper_wallet.profile.accounts.unset_working_account()
    prepare_beekeeper_wallet.profile.save()
    return prepare_beekeeper_wallet.profile
