from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    ALT_WORKING_ACCOUNT1_PASSWORD,
    WITNESS_ACCOUNT_KEY_ALIAS,
    WITNESS_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    WITNESS_ACCOUNT,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    import test_tools as tt
    from beekeepy import AsyncBeekeeper

    from clive_local_tools.cli.types import CLITesterFactory, CLITesterVariant
    from clive_local_tools.types import EnvContextFactory


@pytest.fixture
def _cli_tester_factory(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    beekeeper_local: AsyncBeekeeper,
    node: tt.RawNode,  # noqa: ARG001
    world_with_remote_beekeeper: World,
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

            return CLITester(cli, runner, world_with_remote_beekeeper)

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
            PrivateKeyAliased(value=WITNESS_ACCOUNT.private_key, alias=WITNESS_ACCOUNT_KEY_ALIAS)
        )
        await world_cm.commands.sync_data_with_beekeeper()
        await world_cm.commands.save_profile()  # required for saving imported keys aliases
        await cli_tester_locked.world.switch_profile(world_cm.profile)
    return cli_tester_locked
