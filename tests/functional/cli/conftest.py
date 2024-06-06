from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.constants import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.core.url import Url
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA, run_node

if TYPE_CHECKING:
    import test_tools as tt


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
    world = World(WORKING_ACCOUNT_DATA.account.name)
    await world.setup()
    return world


@pytest.fixture()
async def prepare_beekeeper_wallet(world: World) -> None:
    await CreateWallet(
        app_state=world.app_state,
        beekeeper=world.beekeeper,
        wallet=WORKING_ACCOUNT_DATA.account.name,
        password=WORKING_ACCOUNT_PASSWORD,
    ).execute_with_result()
    world.profile_data.working_account.keys.add_to_import(
        PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
    )
    await world.commands.sync_data_with_beekeeper()


@pytest.fixture()
async def run_testnet(world: World, prepare_beekeeper_wallet: None) -> tt.RawNode:  # noqa: ARG001
    """Will run node from pregenerated block_log and prepare profile."""
    node = run_node()
    await world.node.set_address(Url.parse(node.http_endpoint.as_string()))
    await world.close()
    return node


@pytest.fixture()
async def cli_tester(run_testnet: tt.RawNode) -> CLITester:  # noqa: ARG001
    """Will return CliveTyper and CliRunner from typer.testing module.."""
    # import cli after default profile is set, default values for --profile-name option are set during loading
    from clive.__private.cli.main import cli

    env = {"COLUMNS": f"{TERMINAL_WIDTH}"}
    runner = CliRunner(env=env)
    return CLITester(cli, runner)
