from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING

import pytest
from beekeepy import AsyncBeekeeper, Settings
from typer.testing import CliRunner

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.commands.beekeeper import BeekeeperSaveDetached
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

    import test_tools as tt

    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
async def beekeeper_local() -> AsyncGenerator[AsyncBeekeeper]:
    """CLI tests are remotely connecting to a locally started beekeeper by this fixture."""
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_factory()) as beekeeper_cm:
        bk = beekeeper_cm
        yield bk


@pytest.fixture
async def prepare_profile() -> Profile:
    return Profile.create(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
    )


@pytest.fixture
async def world(beekeeper_local: AsyncBeekeeper) -> World:
    return World(
        settings_or_url=Settings(
            http_endpoint=beekeeper_local.pack().settings.http_endpoint,
            use_existing_session=await (await beekeeper_local.session).token,
        )
    )


@pytest.fixture
async def prepare_beekeeper_wallet(world: World, prepare_profile: Profile) -> AsyncGenerator[World]:
    """Prepare wallet and yield World inside of context manager ready to use."""
    async with world as world_cm:
        await world_cm.switch_profile(prepare_profile)
        await world_cm.commands.create_wallet(password=WORKING_ACCOUNT_PASSWORD)
        await world_cm.commands.sync_state_with_beekeeper()
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
        )
        await world_cm.commands.sync_data_with_beekeeper()
        world_cm.profile.save()  # required for saving imported keys aliases

        beekeeper = world_cm.beekeeper
        http_endpoint = beekeeper.pack().settings.http_endpoint
        assert http_endpoint is not None, "While performing setup of beekeeper, it own address was not set"
        await BeekeeperSaveDetached(
            pid=0, endpoint=http_endpoint.as_string()
        ).execute()  # so that cli commands can refer

        yield world_cm


@pytest.fixture
async def beekeeper(prepare_beekeeper_wallet: World) -> AsyncBeekeeper:
    return prepare_beekeeper_wallet.beekeeper


@pytest.fixture
async def node(node_address_env_context_factory: EnvContextFactory) -> AsyncGenerator[tt.RawNode]:
    node = run_node()
    address = str(node.http_endpoint)
    with node_address_env_context_factory(address):
        yield node


@pytest.fixture
async def cli_tester(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    beekeeper_local: AsyncBeekeeper,
    node: tt.RawNode,  # noqa: ARG001
    prepare_beekeeper_wallet: World,
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
        address = str(beekeeper_local.pack().settings.http_endpoint)
        stack.enter_context(beekeeper_remote_address_env_context_factory(address))
        stack.enter_context(beekeeper_session_token_env_context_factory(await (await beekeeper_local.session).token))
        yield CLITester(cli, runner, prepare_beekeeper_wallet)


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
