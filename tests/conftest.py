from __future__ import annotations

import shutil
from contextlib import ExitStack, contextmanager
from functools import wraps
from typing import TYPE_CHECKING, Generator

import pytest
import test_tools as tt
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403

from clive.__private.before_launch import prepare_before_launch
from clive.__private.core import iwax
from clive.__private.core._thread import thread_pool
from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.beekeeper.handle import Beekeeper
from clive.__private.core.commands.create_profile_encryption_wallet import CreateProfileEncryptionWallet
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.constants.setting_identifiers import DATA_PATH, LOG_PATH, NODE_CHAIN_ID
from clive.__private.core.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.core.url import Url
from clive.__private.core.world import World
from clive.__private.settings import settings
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.data.constants import (
    BEEKEEPER_REMOTE_ADDRESS_ENV_NAME,
    BEEKEEPER_SESSION_TOKEN_ENV_NAME,
    NODE_CHAIN_ID_ENV_NAME,
    TESTNET_CHAIN_ID,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.data.generates import generate_wallet_name, generate_wallet_password
from clive_local_tools.data.models import Keys, WalletInfo
from clive_local_tools.test_doubles.app_state import AppStateUnlocked
from clive_local_tools.testnet_block_log import (
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from clive.__private.core.keys.keys import PrivateKey, PublicKey
    from clive_local_tools.types import BeekeeperSessionTokenEnvContextFactory, SetupWalletsFactory, Wallets


@pytest.fixture(autouse=True, scope="session")
def manage_thread_pool() -> Iterator[None]:
    with thread_pool:
        yield


@pytest.fixture(autouse=True)
def run_prepare_before_launch() -> None:
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

    # set chain id to the testnet one
    settings.set(NODE_CHAIN_ID, TESTNET_CHAIN_ID)

    prepare_before_launch(enable_stream_handlers=True)


@pytest.fixture
def wallet_name() -> str:
    return generate_wallet_name()


@pytest.fixture
def wallet_password() -> str:
    return generate_wallet_password()


@pytest.fixture
def key_pair() -> tuple[PublicKey, PrivateKey]:
    private_key = iwax.generate_private_key()
    public_key = private_key.calculate_public_key()
    return public_key, private_key


@pytest.fixture
async def env_variable_context(
    monkeypatch: pytest.MonkeyPatch,
) -> BeekeeperSessionTokenEnvContextFactory:
    @wraps(env_variable_context)
    @contextmanager
    def __env_variable_context(name: str, value: str) -> Generator[None]:
        monkeypatch.setenv(name, value)
        settings.reload()
        yield
        monkeypatch.delenv(name, raising=False)
        settings.reload()

    return __env_variable_context


@pytest.fixture
async def beekeeper(env_variable_context: BeekeeperSessionTokenEnvContextFactory) -> AsyncIterator[Beekeeper]:
    async with Beekeeper() as beekeeper_cm:
        with ExitStack() as stack:
            stack.enter_context(env_variable_context(NODE_CHAIN_ID_ENV_NAME, TESTNET_CHAIN_ID))
            stack.enter_context(env_variable_context(BEEKEEPER_SESSION_TOKEN_ENV_NAME, beekeeper_cm.token))
            stack.enter_context(
                env_variable_context(BEEKEEPER_REMOTE_ADDRESS_ENV_NAME, str(beekeeper_cm.http_endpoint))
            )
            yield beekeeper_cm


@pytest.fixture
async def prepare_profile(beekeeper: Beekeeper) -> Profile:
    profile = Profile(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(name) for name in WATCHED_ACCOUNTS_NAMES],
    )
    await CreateProfileEncryptionWallet(
        beekeeper=beekeeper, profile_name=profile.name, password=WORKING_ACCOUNT_PASSWORD
    ).execute()
    await CreateWallet(beekeeper=beekeeper, wallet=profile.name, password=WORKING_ACCOUNT_PASSWORD).execute()
    await PersistentStorageService(beekeeper).save_profile(profile)
    return profile


@pytest.fixture
async def prepare_wallet(prepare_profile: Profile) -> WalletInfo:
    private_key = PrivateKeyAliased(
        value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}"
    )
    wallet_info = WalletInfo(
        name=prepare_profile.name, password=WORKING_ACCOUNT_PASSWORD, keys=Keys.from_private_key(private_key)
    )
    async with World() as world_cm:
        world_cm.profile.keys.add_to_import(wallet_info.private_key)
        await world_cm.commands.sync_data_with_beekeeper()
    return wallet_info


# World always needs profile prepared, TUIWorld performs onboarding when profile is not found
@pytest.fixture
async def world(beekeeper: Beekeeper, prepare_profile: Profile, prepare_wallet: WalletInfo) -> AsyncIterator[World]:  # noqa: ARG001
    async with World(beekeeper_remote_endpoint=beekeeper.http_endpoint) as world_cm:
        yield world_cm


@pytest.fixture
async def init_node(world: World) -> AsyncIterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.run()
    await world.node.set_address(Url.parse(init_node.http_endpoint.as_string()))
    yield init_node
    init_node.close()


@pytest.fixture
async def init_node_extra_apis(world: World) -> AsyncIterator[tt.InitNode]:
    init_node = tt.InitNode()
    init_node.config.plugin.append("transaction_status_api")
    init_node.config.plugin.append("account_history_api")
    init_node.config.plugin.append("account_history_rocksdb")
    init_node.run()
    await world.node.set_address(Url.parse(init_node.http_endpoint.as_string()))
    yield init_node
    init_node.close()


@pytest.fixture
def setup_wallets(beekeeper: Beekeeper) -> SetupWalletsFactory:
    @wraps(setup_wallets)
    async def __setup_wallets(count: int, *, import_keys: bool = True, keys_per_wallet: int = 1) -> Wallets:
        wallets = [
            WalletInfo(name=generate_wallet_name(i), password=generate_wallet_password(i), keys=Keys(keys_per_wallet))
            for i in range(count)
        ]
        for wallet in wallets:
            await CreateWallet(beekeeper=beekeeper, wallet=wallet.name, password=wallet.password).execute()

            if import_keys:
                for pairs in wallet.keys.pairs:
                    await ImportKey(
                        app_state=AppStateUnlocked(),
                        wallet=wallet.name,
                        key_to_import=pairs.private_key,
                        beekeeper=beekeeper,
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
