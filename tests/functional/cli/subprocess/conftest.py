from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_KEY_ALIAS
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_DATA

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.profile import Profile


@pytest.fixture
async def prepare_wallet_extra_keys(prepare_wallet: None, _beekeeper_unlocked: Beekeeper) -> None:  # noqa: ARG001
    async with World(beekeeper_remote_endpoint=_beekeeper_unlocked.http_endpoint) as world_cm:
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(
                value=ALT_WORKING_ACCOUNT1_DATA.account.private_key, alias=f"{ALT_WORKING_ACCOUNT1_KEY_ALIAS}"
            )
        )
        await world_cm.commands.sync_data_with_beekeeper()


@pytest.fixture
async def prepare_profile_without_working_account(prepare_profile: Profile, _beekeeper_unlocked: Beekeeper) -> Profile:
    prepare_profile.accounts.unset_working_account()
    await PersistentStorageService(_beekeeper_unlocked).save_profile(prepare_profile)
    return prepare_profile
