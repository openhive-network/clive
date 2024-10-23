from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.data.constants import ALT_WORKING_ACCOUNT1_KEY_ALIAS
from clive_local_tools.data.models import Keys
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_DATA

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.profile import Profile
    from clive_local_tools.data.models import WalletInfo


@pytest.fixture
async def prepare_wallet_extra_keys(prepare_wallet: WalletInfo) -> WalletInfo:
    wallet_info = prepare_wallet
    extra_key = PrivateKeyAliased(
        value=ALT_WORKING_ACCOUNT1_DATA.account.private_key, alias=f"{ALT_WORKING_ACCOUNT1_KEY_ALIAS}"
    )
    pair = Keys.KeysPair(
        public_key=extra_key.calculate_public_key(),
        private_key=extra_key,
    )
    wallet_info.keys.pairs.append(pair)
    async with World() as world_cm:
        world_cm.profile.keys.add_to_import(extra_key)
        await world_cm.commands.sync_data_with_beekeeper()
    return wallet_info


@pytest.fixture
async def prepare_profile_without_working_account(prepare_profile: Profile, beekeeper: Beekeeper) -> Profile:
    prepare_profile.accounts.unset_working_account()
    await PersistentStorageService(beekeeper).save_profile(prepare_profile)
    return prepare_profile
