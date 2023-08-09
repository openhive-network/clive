from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest
import test_tools as tt
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403

from clive.__private.before_launch import prepare_before_launch
from clive.__private.config import settings
from clive.__private.core import iwax
from clive.__private.core._thread import thread_pool
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.world import World
from clive.core.url import Url
from tests import WalletInfo

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.keys.keys import PrivateKey, PublicKey


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

    settings.data_path = working_directory
    settings.log_path = working_directory / "logs"
    prepare_before_launch()


@pytest.fixture()
def wallet_name() -> str:
    return "wallet"


@pytest.fixture()
def wallet_password() -> str:
    return "password"


@pytest.fixture()
def key_pair() -> tuple[PublicKey, PrivateKey]:
    private_key = iwax.generate_private_key()
    public_key = private_key.calculate_public_key()
    return public_key, private_key


@pytest.fixture()
async def world(wallet_name: str) -> AsyncIterator[World]:
    world = World(profile_name=wallet_name)
    yield world
    await world.close()


@pytest.fixture()
def init_node(world: World) -> Iterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.run()
    world.profile_data._node_address = Url.parse(init_node.http_endpoint, protocol="http")
    yield init_node
    init_node.close()


@pytest.fixture()
async def wallet(world: World, wallet_name: str, wallet_password: str) -> WalletInfo:
    await CreateWallet(
        app_state=world.app_state, beekeeper=world.beekeeper, wallet=wallet_name, password=wallet_password
    ).execute()

    return WalletInfo(
        password=wallet_password,
        name=wallet_name,
    )


@pytest.fixture()
def beekeeper(world: World) -> Beekeeper:
    return world.beekeeper
