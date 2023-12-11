from __future__ import annotations

import asyncio
import shutil
from random import randint
from typing import TYPE_CHECKING

import pytest

import test_tools as tt
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403

from clive.__private.config import settings
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.core.world import TextualWorld
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.__private.ui.app import Clive
from clive.core.url import Url

from clive_local_tools.constants import TESTNET_CHAIN_ID

from .constants import *

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


def create_working_account(wallet: tt.Wallet) -> None:
    wallet.create_account(
        WORKING_ACCOUNT.name,
        hives=tt.Asset.Test(100).as_nai(),
        vests=tt.Asset.Test(100).as_nai(),
        hbds=tt.Asset.Tbd(100).as_nai(),
    )


def create_watched_accounts(wallet: tt.Wallet) -> None:
    def random_amount() -> int:
        return randint(1_000, 5_000)

    tt.logger.info("Creating watched accounts...")
    for account in WATCHED_ACCOUNTS:
        wallet.create_account(
            account.name,
            hives=tt.Asset.Test(random_amount()).as_nai(),
            vests=tt.Asset.Test(random_amount()).as_nai(),
            hbds=tt.Asset.Tbd(random_amount()).as_nai(),
        )

async def prepare_profile(node: tt.InitNode) -> None:
    tt.logger.info("Configuring ProfileData for clive")
    settings.set("secrets.node_address", f"http://{node.http_endpoint}")
    settings.set("node.chain_id", TESTNET_CHAIN_ID)

    ProfileData(
        WORKING_ACCOUNT.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT.name),
        watched_accounts=[WatchedAccount(acc.name) for acc in WATCHED_ACCOUNTS],
    ).save()

    async with World(WORKING_ACCOUNT.name) as world:
        password = await CreateWallet(
            app_state=world.app_state,
            beekeeper=world.beekeeper,
            wallet=WORKING_ACCOUNT.name,
            password=WORKING_ACCOUNT.name,
        ).execute_with_result()

        tt.logger.info(f"password for {WORKING_ACCOUNT.name} is: `{password}`")
        world.profile_data.working_account.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT.private_key._value, alias=f"{WORKING_ACCOUNT.name}_key")
        )
        await world.commands.sync_data_with_beekeeper()

@pytest.fixture(scope='package')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='package')
async def prepared_node() -> AsyncIterator[tt.InitNode]:
    node = tt.InitNode()
    node.config.plugin.append("account_history_rocksdb")
    node.config.plugin.append("account_history_api")
    node.config.plugin.append("reputation_api")
    node.config.plugin.append("rc_api")
    node.config.plugin.append("transaction_status_api")
    node.run()

    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
    wallet.api.import_key(node.config.private_key[0])
    create_working_account(wallet)
    create_watched_accounts(wallet)

    shutil.rmtree(settings.data_path, ignore_errors=True)

    await prepare_profile(node)

    world = TextualWorld()
    await world.setup()
    await world.node.set_address(Url.parse(node.http_endpoint, protocol="http"))
    Clive.world = world

    yield node

    node.close()
    wallet.close()
    await world.close()
