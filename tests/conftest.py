from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest
import test_tools as tt
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403

from clive.__private.config import settings
from clive.__private.core import iwax
from clive.__private.core.world import World
from clive.__private.util import prepare_before_launch
from clive.core.url import Url
from tests import WalletInfo

if TYPE_CHECKING:
    from collections.abc import Iterator

    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.storage.mock_database import PrivateKey, PublicKey


@pytest.fixture(autouse=True, scope="function")
def run_prepare_before_launch() -> None:
    working_directory = tt.context.get_current_directory()

    beekeeper_directory = working_directory / "beekeeper"
    if beekeeper_directory.exists():
        shutil.rmtree(beekeeper_directory)

    settings.data_path = working_directory
    settings.log_path = working_directory / "logs"
    prepare_before_launch()


@pytest.fixture
def wallet_name() -> str:
    return "wallet"


@pytest.fixture
def wallet_password() -> str:
    return "password"


@pytest.fixture
def key_pair() -> tuple[PublicKey, PrivateKey]:
    private_key = iwax.generate_private_key()
    public_key = private_key.calculate_public_key()
    return public_key, private_key


@pytest.fixture
def world(wallet_name: str) -> Iterator[World]:
    world = World(profile_name=wallet_name)
    yield world
    world.close()


@pytest.fixture
def init_node(world: World) -> Iterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.run()
    world.profile_data.node_address = Url.parse(init_node.http_endpoint, protocol="http")
    yield init_node
    init_node.close()


@pytest.fixture
def wallet(world: World, wallet_name: str, wallet_password: str) -> WalletInfo:
    world.beekeeper.api.create(wallet_name=wallet_name, password=wallet_password)

    return WalletInfo(
        password=wallet_password,
        name=wallet_name,
    )


@pytest.fixture
def beekeeper(world: World) -> Beekeeper:
    return world.beekeeper
