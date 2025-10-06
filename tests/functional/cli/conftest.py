from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING

import beekeepy as bk
import pytest
from typer.testing import CliRunner

from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    ALT_WORKING_ACCOUNT1_PASSWORD,
    WITNESS_ACCOUNT_KEY_ALIAS,
    WITNESS_ACCOUNT_PASSWORD,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    KNOWN_ACCOUNTS,
    WATCHED_ACCOUNTS_NAMES,
    WITNESS_ACCOUNT,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
    run_node,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    import test_tools as tt
    from beekeepy import AsyncBeekeeper

    from clive.__private.core.profile import Profile
    from clive_local_tools.cli.types import CLITesterFactory, CLITesterVariant
    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
def logger_configuration_factory() -> Callable[[], None]:
    def _logger_configuration_factory() -> None:
        logger.setup(enable_textual=False)

    return _logger_configuration_factory


@pytest.fixture
async def beekeeper_local() -> AsyncGenerator[AsyncBeekeeper]:
    """CLI tests are remotely connecting to a locally started beekeeper by this fixture."""
    async with await bk.AsyncBeekeeper.factory(
        settings=safe_settings.beekeeper.settings_local_factory()
    ) as beekeeper_cm:
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
    await world_cli.set_address(node.http_endpoint)
    address = str(node.http_endpoint)
    with node_address_env_context_factory(address):
        yield node


@pytest.fixture
def _cli_tester_factory(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    beekeeper_local: AsyncBeekeeper,
    node: tt.RawNode,  # noqa: ARG001
    world_cli: World,
) -> CLITesterFactory:
    """Factory that creates cli_tester depending on desired variant."""

    async def factory(variant: CLITesterVariant) -> AsyncGenerator[CLITester]:
        # import cli after default values for options/arguments are set
        from clive.__private.cli.main import cli  # noqa: PLC0415

        env = {"COLUMNS": f"{TERMINAL_WIDTH}"}
        runner = CliRunner(env=env)

        async def create_cli_tester_unlocked(stack: ExitStack) -> CLITester:
            address = str(beekeeper_local.http_endpoint)
            token = await (await beekeeper_local.session).token

            stack.enter_context(beekeeper_remote_address_env_context_factory(address))
            stack.enter_context(beekeeper_session_token_env_context_factory(token))

            return CLITester(cli, runner, world_cli)

        with ExitStack() as stack:
            cli_tester = await create_cli_tester_unlocked(stack)

            if variant == "locked":
                await cli_tester.world.commands.lock()
                # cannot save profile when it is locked because encryption is not possible
                cli_tester.world.profile.skip_saving()
            elif variant == "without remote address":
                stack.enter_context(beekeeper_remote_address_env_context_factory(None))
            elif variant == "without session token":
                stack.enter_context(beekeeper_session_token_env_context_factory(None))
            elif variant != "unlocked":
                pytest.fail(f"Invalid parameter for cli_tester factory: {variant!r}")

            yield cli_tester

    return factory


@pytest.fixture
async def cli_tester_variant(_cli_tester_factory: CLITesterFactory, request: pytest.FixtureRequest) -> CLITester:
    """Variables depend on params."""
    return await anext(_cli_tester_factory(request.param))


@pytest.fixture
async def cli_tester(_cli_tester_factory: CLITesterFactory) -> CLITester:
    """
    Will return CliveTyper and CliRunner from typer.testing module.

    Environment variable for session token is set.
    Environment variable for beekeeper remote address is set.
    """
    return await anext(_cli_tester_factory("unlocked"))


@pytest.fixture
async def cli_tester_locked(_cli_tester_factory: CLITesterFactory) -> CLITester:
    """Session token and remote address are set in the environment variables. Profile is locked."""
    return await anext(_cli_tester_factory("locked"))


@pytest.fixture
async def cli_tester_without_remote_address(_cli_tester_factory: CLITesterFactory) -> CLITester:
    """Remote address not set in environment variable."""
    return await anext(_cli_tester_factory("without remote address"))


@pytest.fixture
async def cli_tester_without_session_token(_cli_tester_factory: CLITesterFactory) -> CLITester:
    """Session token is not set in environment variable."""
    return await anext(_cli_tester_factory("without session token"))


@pytest.fixture
async def cli_tester_locked_with_second_profile(cli_tester_locked: CLITester) -> CLITester:
    """There are two profiles and cli_tester is locked."""
    async with World() as world_cm:
        await world_cm.create_new_profile_with_wallets(ALT_WORKING_ACCOUNT1_NAME, ALT_WORKING_ACCOUNT1_PASSWORD)
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(
                value=ALT_WORKING_ACCOUNT1_DATA.account.private_key, alias=f"{ALT_WORKING_ACCOUNT1_KEY_ALIAS}"
            )
        )
        await world_cm.commands.sync_data_with_beekeeper()
        await world_cm.commands.save_profile()  # required for saving imported keys aliases
        await world_cm.commands.lock()
        world_cm.profile.skip_saving()  # cannot save profile when it is locked because encryption is not possible
    return cli_tester_locked


@pytest.fixture
async def cli_tester_unlocked_with_witness_profile(cli_tester_locked: CLITester) -> CLITester:
    """There is witness profile with witness key imported and cli_tester is unlocked."""
    async with World() as world_cm:
        await world_cm.create_new_profile_with_wallets(
            name=WITNESS_ACCOUNT.name,
            password=WITNESS_ACCOUNT_PASSWORD,
            working_account=WITNESS_ACCOUNT.name,
        )
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WITNESS_ACCOUNT.private_key, alias=f"{WITNESS_ACCOUNT_KEY_ALIAS}")
        )
        await world_cm.commands.sync_data_with_beekeeper()
        await world_cm.commands.save_profile()  # required for saving imported keys aliases
        await cli_tester_locked.world.switch_profile(world_cm.profile)
    return cli_tester_locked
