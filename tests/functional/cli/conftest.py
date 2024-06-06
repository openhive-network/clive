from __future__ import annotations

import pytest
import test_tools as tt
from typer.testing import CliRunner

from clive.__private.config import settings
from clive.__private.core.constants import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA, run_node


@pytest.fixture()
async def prepare_profile() -> ProfileData:
    profile_data = ProfileData(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
    )
    profile_data.save()
    return profile_data


@pytest.fixture()
async def world(prepare_profile: ProfileData) -> World:  # noqa: ARG001
    return World()  # will load last profile by default


@pytest.fixture()
async def prepare_beekeeper_wallet(world: World) -> None:
    async with world:
        password = (await world.commands.create_wallet(password=WORKING_ACCOUNT_PASSWORD)).result_or_raise
        tt.logger.info(f"password for {WORKING_ACCOUNT_DATA.account.name} is: `{password}`")

        world.profile_data.working_account.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
        )
        await world.commands.sync_data_with_beekeeper()


@pytest.fixture()
async def node() -> tt.RawNode:
    node = run_node()
    settings["secrets.node_address"] = node.http_endpoint.as_string()
    return node


@pytest.fixture()
async def cli_tester(node: tt.RawNode, prepare_beekeeper_wallet: None) -> CLITester:  # noqa: ARG001
    """Will return CliveTyper and CliRunner from typer.testing module.."""
    # import cli after default profile is set, default values for --profile-name option are set during loading
    from clive.__private.cli.main import cli

    env = {"COLUMNS": f"{TERMINAL_WIDTH}"}
    runner = CliRunner(env=env)
    return CLITester(cli, runner)
