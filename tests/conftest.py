from __future__ import annotations

import os
import shutil
from contextlib import contextmanager, suppress
from functools import wraps
from typing import TYPE_CHECKING, Generator

import pytest
import test_tools as tt
from beekeepy import AsyncBeekeeper
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403

from clive.__private.before_launch import prepare_before_launch
from clive.__private.core import iwax
from clive.__private.core._thread import thread_pool
from clive.__private.core.commands.abc.command_profile_encryption import CommandProfileEncryptionError
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.constants.setting_identifiers import DATA_PATH, LOG_LEVEL_1ST_PARTY, LOG_LEVELS, LOG_PATH
from clive.__private.core.world import World
from clive.__private.settings import settings
from clive_local_tools.data.constants import (
    BEEKEEPER_REMOTE_ADDRESS_ENV_NAME,
    BEEKEEPER_SESSION_TOKEN_ENV_NAME,
    NODE_CHAIN_ID_ENV_NAME,
    SECRETS_NODE_ADDRESS_ENV_NAME,
    TESTNET_CHAIN_ID,
)
from clive_local_tools.data.generates import generate_wallet_name, generate_wallet_password
from clive_local_tools.data.models import Keys, WalletInfo

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from beekeepy import AsyncBeekeeper

    from clive.__private.core.keys.keys import PrivateKey, PublicKey
    from clive.__private.core.profile import Profile
    from clive_local_tools.types import EnvContextFactory, GenericEnvContextFactory, SetupWalletsFactory, Wallets


@pytest.fixture(autouse=True, scope="session")
def manage_thread_pool() -> Iterator[None]:
    with thread_pool:
        yield


@pytest.fixture
def testnet_chain_id_env_context(generic_env_context_factory: GenericEnvContextFactory) -> Generator[None]:
    chain_id_env_context_factory = generic_env_context_factory(NODE_CHAIN_ID_ENV_NAME)
    with chain_id_env_context_factory(TESTNET_CHAIN_ID):
        yield


@pytest.fixture(autouse=True)
def run_prepare_before_launch(testnet_chain_id_env_context: None) -> None:  # noqa: ARG001
    settings.reload()
    working_directory = tt.context.get_current_directory() / "clive"

    beekeeper_directory = working_directory / "beekeeper"
    if beekeeper_directory.exists():
        shutil.rmtree(beekeeper_directory)

    profile_data_directory = working_directory / "data"
    if profile_data_directory.exists():
        shutil.rmtree(profile_data_directory)

    settings.set(DATA_PATH, working_directory)
    log_path = working_directory / "logs"
    settings.set(LOG_PATH, log_path)

    settings.set(LOG_LEVELS, ["DEBUG"])
    settings.set(LOG_LEVEL_1ST_PARTY, "DEBUG")

    prepare_before_launch(enable_stream_handlers=True)


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
    with suppress(CommandProfileEncryptionError):
        async with World() as world_cm:
            yield world_cm


@pytest.fixture
async def prepare_profile_with_wallet(world: World, wallet_name: str, wallet_password: str) -> Profile:
    await world.create_new_profile_with_beekeeper_wallet(wallet_name, wallet_password)
    return world.profile


@pytest.fixture
async def init_node(
    prepare_profile_with_wallet: Profile,
    node_address_env_context_factory: EnvContextFactory,
    world: World,
) -> AsyncIterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.config.log_json_rpc = "jsonrpc"
    init_node.run()
    await world.node.set_address(init_node.http_endpoint)
    prepare_profile_with_wallet._set_node_address(init_node.http_endpoint)
    await world.commands.save_profile()
    address = str(init_node.http_endpoint)
    with node_address_env_context_factory(address):
        yield init_node


@pytest.fixture
async def init_node_extra_apis(
    prepare_profile_with_wallet: Profile,
    node_address_env_context_factory: EnvContextFactory,
    world: World,
) -> AsyncIterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.config.plugin.append("transaction_status_api")
    init_node.config.plugin.append("account_history_api")
    init_node.config.plugin.append("account_history_rocksdb")
    init_node.run()
    await world.node.set_address(init_node.http_endpoint)
    prepare_profile_with_wallet._set_node_address(init_node.http_endpoint)
    await world.commands.save_profile()
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
            await CreateWallet(
                app_state=world.app_state,
                session=world._session_ensure,
                wallet_name=wallet.name,
                password=wallet.password,
            ).execute()

            if import_keys:
                for pairs in wallet.keys.pairs:
                    await ImportKey(
                        unlocked_wallet=world._unlocked_wallet_ensure,
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


@pytest.fixture
def generic_env_context_factory(monkeypatch: pytest.MonkeyPatch) -> GenericEnvContextFactory:
    def factory(env_name: str) -> EnvContextFactory:
        def _setdelenv(value: str | None) -> None:
            monkeypatch.setenv(env_name, value) if value else monkeypatch.delenv(env_name, raising=False)
            settings.reload()

        @wraps(factory)
        @contextmanager
        def impl(value: str | None) -> Generator[None]:
            previous_value = os.getenv(env_name)
            _setdelenv(value)
            yield
            _setdelenv(previous_value)

        return impl

    return factory


@pytest.fixture
def beekeeper_remote_address_env_context_factory(
    generic_env_context_factory: GenericEnvContextFactory,
) -> EnvContextFactory:
    return generic_env_context_factory(BEEKEEPER_REMOTE_ADDRESS_ENV_NAME)


@pytest.fixture
def beekeeper_session_token_env_context_factory(
    generic_env_context_factory: GenericEnvContextFactory,
) -> EnvContextFactory:
    return generic_env_context_factory(BEEKEEPER_SESSION_TOKEN_ENV_NAME)


@pytest.fixture
def node_address_env_context_factory(generic_env_context_factory: GenericEnvContextFactory) -> EnvContextFactory:
    return generic_env_context_factory(SECRETS_NODE_ADDRESS_ENV_NAME)
