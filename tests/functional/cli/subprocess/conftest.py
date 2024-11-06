from __future__ import annotations

import pytest

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
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


@pytest.fixture
async def prepare_profile_without_working_account(prepare_profile: Profile) -> Profile:
    prepare_profile.accounts.unset_working_account()
    prepare_profile.save()
    return prepare_profile


@pytest.fixture
async def alt_prepare_profile() -> Profile:
    profile = Profile.create(
        ALT_WORKING_ACCOUNT1_NAME,
        working_account=WorkingAccount(name=ALT_WORKING_ACCOUNT1_NAME),
        watched_accounts=[WatchedAccount(name) for name in WATCHED_ACCOUNTS_NAMES],
    )
    profile.save()
    return profile


@pytest.fixture
async def alt_world(alt_prepare_profile: Profile) -> World:  # noqa: ARG001
    return World(profile_name=ALT_WORKING_ACCOUNT1_NAME)  # we must point to alternative profile


@pytest.fixture
async def alt_prepare_beekeeper_wallet(alt_world: World) -> None:
    async with alt_world as alt_world_cm:
        await alt_world_cm.commands.create_wallet(password=ALT_WORKING_ACCOUNT1_PASSWORD)

        alt_world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}"),
            PrivateKeyAliased(
                value=ALT_WORKING_ACCOUNT1_DATA.account.private_key, alias=f"{ALT_WORKING_ACCOUNT1_KEY_ALIAS}"
            ),
        )
        await alt_world_cm.commands.sync_data_with_beekeeper()
