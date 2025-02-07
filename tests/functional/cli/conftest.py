from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING

import pytest
from beekeepy import AsyncBeekeeper
from typer.testing import CliRunner

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.core.world import World
from clive.__private.settings import safe_settings
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA, run_node

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from typing import AsyncIterator

    import test_tools as tt

    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
async def beekeeper_local() -> AsyncGenerator[AsyncBeekeeper]:
    """CLI tests are remotely connecting to a locally started beekeeper by this fixture."""
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory()) as beekeeper_cm:
        yield beekeeper_cm


@pytest.fixture
async def prepare_profile() -> Profile:
    return Profile.create(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
    )


@pytest.fixture
async def world(beekeeper_local: AsyncBeekeeper) -> AsyncIterator[World]:
    token = await (await beekeeper_local.session).token

    world = World()
    world.beekeeper_settings.http_endpoint = beekeeper_local.http_endpoint
    world.beekeeper_settings.use_existing_session = token
    async with world as world_cm:
        yield world_cm


@pytest.fixture
async def prepare_profile_with_wallet(world: World) -> Profile:
    """Prepare profile and wallets."""
    await world.create_new_profile_with_beekeeper_wallet(
        name=WORKING_ACCOUNT_DATA.account.name,
        password=WORKING_ACCOUNT_PASSWORD,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
    )
    await world.commands.sync_state_with_beekeeper()
    world.profile.keys.add_to_import(
        PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
    )
    await world.commands.sync_data_with_beekeeper()
    await world.save_profile()  # required for saving imported keys aliases
    return world.profile


@pytest.fixture
async def node(
    node_address_env_context_factory: EnvContextFactory,
    world: World,
    prepare_profile_with_wallet: Profile,  # noqa: ARG001
) -> AsyncGenerator[tt.RawNode]:
    node = run_node()
    await world.node.set_address(node.http_endpoint)
    address = str(node.http_endpoint)
    with node_address_env_context_factory(address):
        yield node


@pytest.fixture
async def cli_tester(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    beekeeper_local: AsyncBeekeeper,
    node: tt.RawNode,  # noqa: ARG001
    world: World,
) -> AsyncGenerator[CLITester]:
    """
    Will return CliveTyper and CliRunner from typer.testing module.

    Environment variable for session token is set.
    Environment variable for beekeeper remote address is set.
    """
    # import cli after default values for options/arguments are set
    from clive.__private.cli.main import cli

    env = {"COLUMNS": f"{TERMINAL_WIDTH}"}
    runner = CliRunner(env=env)
    with ExitStack() as stack:
        address = str(beekeeper_local.http_endpoint)
        stack.enter_context(beekeeper_remote_address_env_context_factory(address))
        stack.enter_context(beekeeper_session_token_env_context_factory(await (await beekeeper_local.session).token))
        yield CLITester(cli, runner, world)


@pytest.fixture
async def cli_tester_locked(cli_tester: CLITester) -> CLITester:
    """Token is set in environment variable. Beekeeper session is locked."""
    await cli_tester.world.commands.lock_all()
    return cli_tester


@pytest.fixture
async def cli_tester_without_session_token(
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    cli_tester: CLITester,
) -> AsyncGenerator[CLITester]:
    """Token is not set in environment variable."""
    with beekeeper_session_token_env_context_factory(None):
        yield cli_tester
