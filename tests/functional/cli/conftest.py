from __future__ import annotations

from collections.abc import Callable
from contextlib import ExitStack
from typing import TYPE_CHECKING

import pytest
from beekeepy import AsyncBeekeeper
from typer.testing import CliRunner

from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    KNOWN_ACCOUNTS,
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
    run_node,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    import test_tools as tt

    from clive.__private.core.profile import Profile
    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
def logger_configuration_factory() -> Callable[[], None]:
    def _logger_configuration_factory() -> None:
        logger.setup(enable_textual=False)

    return _logger_configuration_factory


@pytest.fixture
async def beekeeper_local() -> AsyncGenerator[AsyncBeekeeper]:
    """CLI tests are remotely connecting to a locally started beekeeper by this fixture."""
    async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory()) as beekeeper_cm:
        yield beekeeper_cm


@pytest.fixture
async def world_cli(beekeeper_local: AsyncBeekeeper) -> AsyncGenerator[World]:
    token = await (await beekeeper_local.session).token

    world = World()
    world.beekeeper_manager.settings.http_endpoint = beekeeper_local.http_endpoint
    world.beekeeper_manager.settings.use_existing_session = token
    async with world as world_cm:
        yield world_cm


@pytest.fixture
async def _prepare_profile_with_wallet_cli(world_cli: World) -> Profile:
    """Prepare profile and wallets using remote beekeeper."""
    await world_cli.create_new_profile_with_wallets(
        name=WORKING_ACCOUNT_NAME,
        password=WORKING_ACCOUNT_PASSWORD,
        working_account=WORKING_ACCOUNT_NAME,
        watched_accounts=WATCHED_ACCOUNTS_NAMES,
        known_accounts=KNOWN_ACCOUNTS,
    )
    await world_cli.commands.sync_state_with_beekeeper()
    world_cli.profile.keys.add_to_import(
        PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
    )
    await world_cli.commands.sync_data_with_beekeeper()
    await world_cli.commands.save_profile()  # required for saving imported keys aliases
    return world_cli.profile


@pytest.fixture
async def node(
    node_address_env_context_factory: EnvContextFactory, world_cli: World, _prepare_profile_with_wallet_cli: Profile
) -> AsyncGenerator[tt.RawNode]:
    node = run_node()
    await world_cli.node.set_address(node.http_endpoint)
    address = str(node.http_endpoint)
    with node_address_env_context_factory(address):
        yield node


@pytest.fixture
async def cli_tester(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    beekeeper_local: AsyncBeekeeper,
    node: tt.RawNode,  # noqa: ARG001
    world_cli: World,
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
        yield CLITester(cli, runner, world_cli)


@pytest.fixture
async def cli_tester_locked(cli_tester: CLITester) -> CLITester:
    """Token is set in environment variable. Beekeeper session is locked."""
    await cli_tester.world.commands.lock()
    cli_tester.world.profile.skip_saving()  # cannot save profile when it is locked because encryption is not possible
    return cli_tester


@pytest.fixture
async def cli_tester_without_session_token(
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    cli_tester: CLITester,
) -> AsyncGenerator[CLITester]:
    """Token is not set in environment variable."""
    with beekeeper_session_token_env_context_factory(None):
        yield cli_tester
