from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

import pytest
import test_tools as tt
from beekeepy import AsyncBeekeeper
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403

from clive.__private.core import iwax
from clive.__private.core.commands.create_profile_wallets import CreateProfileWallets
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.world import World
from clive_local_tools.data.generates import generate_wallet_name, generate_wallet_password
from clive_local_tools.data.models import Keys, WalletInfo

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from beekeepy import AsyncBeekeeper

    from clive.__private.core.keys.keys import PrivateKey, PublicKey
    from clive.__private.core.profile import Profile
    from clive_local_tools.types import EnvContextFactory, SetupWalletsFactory, Wallets


@pytest.fixture
def wallet_name() -> str:
    return "fixture_wallet_name"


@pytest.fixture
def wallet_password() -> str:
    return "fixture_wallet_password"


@pytest.fixture
def key_pair() -> tuple[PublicKey, PrivateKey]:
    private_key = iwax.generate_private_key()
    public_key = private_key.calculate_public_key()
    return public_key, private_key


@pytest.fixture
async def world() -> AsyncIterator[World]:
    async with World() as world_cm:
        yield world_cm


@pytest.fixture
async def prepare_profile_with_wallet(world: World, wallet_name: str, wallet_password: str) -> Profile:
    await world.create_new_profile_with_wallets(wallet_name, wallet_password)
    return world.profile


@pytest.fixture
async def init_node(
    prepare_profile_with_wallet: Profile,  # noqa: ARG001
    node_address_env_context_factory: EnvContextFactory,
    world: World,
) -> AsyncIterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.config.log_json_rpc = "jsonrpc"
    init_node.run()
    await world.node.set_address(init_node.http_endpoint)
    address = str(init_node.http_endpoint)
    with node_address_env_context_factory(address):
        yield init_node


@pytest.fixture
async def init_node_extra_apis(
    prepare_profile_with_wallet: Profile,  # noqa: ARG001
    node_address_env_context_factory: EnvContextFactory,
    world: World,
) -> AsyncIterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.config.plugin.append("transaction_status_api")
    init_node.config.plugin.append("account_history_api")
    init_node.config.plugin.append("account_history_rocksdb")
    init_node.run()
    await world.node.set_address(init_node.http_endpoint)
    address = str(init_node.http_endpoint)
    with node_address_env_context_factory(address):
        yield init_node


@pytest.fixture
def beekeeper(world: World) -> AsyncBeekeeper:
    return world.beekeeper


@pytest.fixture
def setup_wallets(world: World) -> SetupWalletsFactory:
    @wraps(setup_wallets)
    async def __setup_wallets(count: int, *, import_keys: bool = True, keys_per_wallet: int = 1) -> Wallets:
        wallets = [
            WalletInfo(name=generate_wallet_name(i), password=generate_wallet_password(i), keys=Keys(keys_per_wallet))
            for i in range(count)
        ]
        for wallet in wallets:
            await CreateProfileWallets(
                app_state=world.app_state,
                session=world._session_ensure,
                profile_name=wallet.name,
                password=wallet.password,
            ).execute()

            if import_keys:
                for pairs in wallet.keys.pairs:
                    await ImportKey(
                        unlocked_wallet=world.wallets.user_wallet,
                        key_to_import=pairs.private_key,
                    ).execute()
        return wallets

    return __setup_wallets


@pytest.fixture
async def wallet(setup_wallets: SetupWalletsFactory) -> WalletInfo:
    """Will return beekeeper created wallet with 1 key-pair already imported."""
    wallets = await setup_wallets(1, import_keys=True, keys_per_wallet=1)
    return wallets[0]


@pytest.fixture
async def wallet_key_to_import(setup_wallets: SetupWalletsFactory) -> WalletInfo:
    """Will return beekeeper created wallet with 1 key-pair ready to import."""
    wallets = await setup_wallets(1, import_keys=False, keys_per_wallet=1)
    return wallets[0]


@pytest.fixture
async def wallet_no_keys(setup_wallets: SetupWalletsFactory) -> WalletInfo:
    """Will return beekeeper created wallet with no keys available."""
    wallets = await setup_wallets(1, import_keys=False, keys_per_wallet=0)
    return wallets[0]
