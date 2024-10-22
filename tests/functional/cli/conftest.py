from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.create_profile_encryption_wallet import CreateProfileEncryptionWallet
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.lock import Lock
from clive.__private.core.commands.unlock import Unlock
from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS
from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.core.world import World
from clive.__private.settings import settings
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    BEEKEEPER_REMOTE_ADDRESS_ENV_NAME,
    BEEKEEPER_SESSION_TOKEN_ENV_NAME,
    NODE_CHAIN_ID_ENV_NAME,
    TESTNET_CHAIN_ID,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    run_node,
)

if TYPE_CHECKING:
    from typing import AsyncIterator

    import test_tools as tt

    from clive_local_tools.types import BeekeeperSessionTokenEnvContextFactory


@pytest.fixture
async def beekeeper_with_session(
    env_variable_context: BeekeeperSessionTokenEnvContextFactory,
) -> AsyncIterator[Beekeeper]:
    async with Beekeeper() as beekeeper_cm:
        with contextlib.ExitStack() as stack:
            stack.enter_context(env_variable_context(NODE_CHAIN_ID_ENV_NAME, TESTNET_CHAIN_ID))
            stack.enter_context(env_variable_context(BEEKEEPER_SESSION_TOKEN_ENV_NAME, beekeeper_cm.token))
            stack.enter_context(
                env_variable_context(BEEKEEPER_REMOTE_ADDRESS_ENV_NAME, str(beekeeper_cm.http_endpoint))
            )
            yield beekeeper_cm


@pytest.fixture
async def prepare_profile(beekeeper_with_session: Beekeeper) -> Profile:
    profile = Profile(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(name) for name in WATCHED_ACCOUNTS_NAMES],
    )
    await CreateProfileEncryptionWallet(
        beekeeper=beekeeper_with_session, profile_name=profile.name, password=WORKING_ACCOUNT_PASSWORD
    ).execute()
    await CreateWallet(
        beekeeper=beekeeper_with_session, wallet=profile.name, password=WORKING_ACCOUNT_PASSWORD
    ).execute()
    await PersistentStorageService(beekeeper_with_session).save_profile(profile)
    return profile


@pytest.fixture
async def prepare_wallet(beekeeper_with_session: Beekeeper, prepare_profile: Profile) -> None:  # noqa: ARG001
    async with World(beekeeper_remote_endpoint=beekeeper_with_session.http_endpoint) as world_cm:
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
        )
        await world_cm.commands.sync_data_with_beekeeper()


@pytest.fixture
async def _beekeeper_locked(
    prepare_profile: Profile,
    prepare_wallet: None,  # noqa: ARG001
    beekeeper_with_session: Beekeeper,
) -> Beekeeper:
    wallet_name = prepare_profile.name
    await Lock(beekeeper=beekeeper_with_session, wallet=wallet_name).execute()
    return beekeeper_with_session


@pytest.fixture
async def _beekeeper_unlocked(
    prepare_profile: Profile,
    prepare_wallet: None,  # noqa: ARG001
    _beekeeper_locked: Beekeeper,
) -> Beekeeper:
    wallet_name = prepare_profile.name
    await Unlock(beekeeper=_beekeeper_locked, wallet=wallet_name, password=WORKING_ACCOUNT_PASSWORD).execute()
    return _beekeeper_locked


@pytest.fixture
async def node() -> tt.RawNode:
    node = run_node()
    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())
    return node


@pytest.fixture
async def cli_tester_with_session_token_locked(
    node: tt.RawNode,  # noqa: ARG001
    prepare_profile: Profile,  # noqa: ARG001
    prepare_wallet: None,  # noqa: ARG001
    _beekeeper_locked: Beekeeper,
) -> CLITester:
    """Will return CliveTyper and CliRunner from typer.testing module, beekeeper is locked."""
    # import cli after default profile is set, default values for --profile-name option are set during loading
    from clive.__private.cli.main import cli

    env = {"COLUMNS": f"{TERMINAL_WIDTH}"}
    runner = CliRunner(env=env)
    return CLITester(cli, runner)


@pytest.fixture
async def cli_tester(
    cli_tester_with_session_token_locked: CLITester,
    _beekeeper_unlocked: Beekeeper,
) -> CLITester:
    """Will return CliveTyper and CliRunner from typer.testing module, beekeeper is unlocked."""
    return cli_tester_with_session_token_locked
