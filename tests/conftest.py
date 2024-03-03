from __future__ import annotations

import os
os.environ["HIVE_BUILD_ROOT_PATH"] = "/workspace/build"

import shutil
from functools import wraps
from typing import TYPE_CHECKING

import pytest
import test_tools as tt
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403

from clive.__private.before_launch import prepare_before_launch
from clive.__private.config import settings
from clive.__private.core import iwax
from clive.__private.core._thread import thread_pool
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.world import World
from clive.models.aliased import Url
from clive_local_tools.data.constants import TESTNET_CHAIN_ID
from clive_local_tools.data.generates import generate_wallet_name, generate_wallet_password
from clive_local_tools.data.models import Keys, WalletInfo

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from clive.__private.core.keys.keys import PrivateKey, PublicKey
    from clive.models.aliased import Beekeeper
    from clive_local_tools.data.types import WalletGeneratorT


@pytest.fixture(autouse=True, scope="session")
def manage_thread_pool() -> Iterator[None]:
    with thread_pool:
        yield


@pytest.fixture(autouse=True)
def run_prepare_before_launch() -> None:
    working_directory = tt.context.get_current_directory()

    beekeeper_directory = working_directory / "beekeeper"
    if beekeeper_directory.exists():
        shutil.rmtree(beekeeper_directory)

    profile_data_directory = working_directory / "data"
    if profile_data_directory.exists():
        shutil.rmtree(profile_data_directory)

    settings.data_path = working_directory
    settings.log_path = working_directory / "logs"

    # set chain id to the testnet one
    settings.set("node.chain_id", TESTNET_CHAIN_ID)

    prepare_before_launch(enable_stream_handlers=True)


@pytest.fixture()
def wallet_name() -> str:
    return generate_wallet_name()


@pytest.fixture()
def wallet_password() -> str:
    return generate_wallet_password()


@pytest.fixture()
def key_pair() -> tuple[PublicKey, PrivateKey]:
    private_key = iwax.generate_private_key()
    public_key = private_key.calculate_public_key()
    return public_key, private_key


@pytest.fixture()
async def world(wallet_name: str) -> AsyncIterator[World]:
    async with World(profile_name=wallet_name) as world:
        yield world


@pytest.fixture()
async def init_node(world: World) -> AsyncIterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.run()
    world.node.http_endpoint = Url(init_node.http_endpoint.as_string())
    yield init_node
    init_node.close()


@pytest.fixture()
async def init_node_extra_apis(world: World) -> AsyncIterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.config.plugin.append("transaction_status_api")
    init_node.config.plugin.append("account_history_api")
    init_node.config.plugin.append("account_history_rocksdb")
    init_node.run()
    world.node.http_endpoint = Url(init_node.http_endpoint.as_string())
    yield init_node
    init_node.close()


@pytest.fixture()
def beekeeper(world: World) -> Beekeeper:
    return world.beekeeper


@pytest.fixture()
def setup_wallet(world: World) -> WalletGeneratorT:
    @wraps(setup_wallet)
    async def __setup_wallet(*, import_keys: bool = True, keys_per_wallet: int = 1) -> WalletInfo:
        wallet = WalletInfo(name=generate_wallet_name(0), password=generate_wallet_password(0), keys=Keys(keys_per_wallet))
        unlocked_wallet = await CreateWallet(
            app_state=world.app_state, session=world.session, wallet=wallet.name, password=wallet.password
        ).execute_with_result()
        world.wallet = unlocked_wallet

        if import_keys:
            for pairs in wallet.keys.pairs:
                await ImportKey(
                    app_state=world.app_state, key_to_import=pairs.private_key, wallet=unlocked_wallet
                ).execute()
        return wallet

    return __setup_wallet


@pytest.fixture()
async def wallet(setup_wallet: WalletGeneratorT) -> WalletInfo:
    """Will return beekeeper created wallet with 1 key-pair already imported."""
    return await setup_wallet(import_keys=True, keys_per_wallet=1)

@pytest.fixture()
async def wallet_key_to_import(setup_wallet: WalletGeneratorT) -> WalletInfo:
    """Will return beekeeper created wallet with 1 key-pair ready to import."""
    return await setup_wallet(import_keys=False, keys_per_wallet=1)


@pytest.fixture()
async def wallet_no_keys(setup_wallet: WalletGeneratorT) -> WalletInfo:
    """Will return beekeeper created wallet with no keys available."""
    return await setup_wallet(import_keys=False, keys_per_wallet=0)
