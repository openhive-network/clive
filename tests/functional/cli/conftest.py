from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.create_profile_encryption_wallet import CreateProfileEncryptionWallet
from clive.__private.core.commands.create_wallet import CreateWallet
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
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_DATA,
    run_node,
)

if TYPE_CHECKING:
    from typing import AsyncIterator

    import test_tools as tt

    from clive_local_tools.types import BeekeeperSessionTokenEnvContextFactory


@pytest.fixture
async def beekeeper_remote(
    env_variable_context: BeekeeperSessionTokenEnvContextFactory,
) -> AsyncIterator[Beekeeper]:
    async with Beekeeper() as beekeeper_cm:
        with contextlib.ExitStack() as stack:
            stack.enter_context(env_variable_context(BEEKEEPER_SESSION_TOKEN_ENV_NAME, beekeeper_cm.token))
            stack.enter_context(
                env_variable_context(BEEKEEPER_REMOTE_ADDRESS_ENV_NAME, str(beekeeper_cm.http_endpoint))
            )
            yield beekeeper_cm


@pytest.fixture
async def prepare_profile(beekeeper_remote: Beekeeper) -> Profile:
    profile = Profile(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
    )
    await CreateProfileEncryptionWallet(
        beekeeper=beekeeper_remote,
        profile=profile,
        password=WORKING_ACCOUNT_PASSWORD,
    ).execute_with_result()
    await CreateWallet(
        beekeeper=beekeeper_remote,
        wallet=profile.name,
        password=WORKING_ACCOUNT_PASSWORD,
    ).execute_with_result()
    await PersistentStorageService(beekeeper_remote).save_profile(profile)
    return profile


@pytest.fixture
async def world(beekeeper_remote: Beekeeper, prepare_profile: Profile) -> World:
    return World(profile_name=prepare_profile.name, beekeeper_remote_endpoint=beekeeper_remote.http_endpoint)


@pytest.fixture
async def prepare_beekeeper_wallet(world: World) -> None:
    async with world as world_cm:
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
        )
        await world_cm.commands.sync_data_with_beekeeper()


@pytest.fixture
async def node() -> tt.RawNode:
    node = run_node()
    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())
    return node


@pytest.fixture
async def cli_tester(
    node: tt.RawNode,  # noqa: ARG001
    prepare_profile: Profile,  # noqa: ARG001
    prepare_beekeeper_wallet: None,  # noqa: ARG001
) -> CLITester:
    """Will return CliveTyper and CliRunner from typer.testing module.."""
    # import cli after default profile is set, default values for --profile-name option are set during loading
    from clive.__private.cli.main import cli

    env = {"COLUMNS": f"{TERMINAL_WIDTH}"}
    runner = CliRunner(env=env)
    return CLITester(cli, runner)


@pytest.fixture
async def cli_tester_with_session_token_locked(
    beekeeper_remote: Beekeeper,
    cli_tester: CLITester,
) -> CLITester:
    await beekeeper_remote.api.lock_all()
    return cli_tester
