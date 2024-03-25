from __future__ import annotations

import pytest
import test_tools as tt
from typer.testing import CliRunner

from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.core.url import Url
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    CREATOR_ACCOUNT,
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_HBD_LIQUID_BALANCE,
    WORKING_ACCOUNT_HIVE_LIQUID_BALANCE,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
    WORKING_ACCOUNT_VEST_BALANCE,
)
from clive_local_tools.testnet_block_log import run_node


@pytest.fixture(autouse=True)
async def run_testnet() -> None:
    """Will run node from pregenerated block_log and prepare profile."""
    node = run_node()

    ProfileData(
        WORKING_ACCOUNT.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT.name),
        watched_accounts=[WatchedAccount(acc.name) for acc in WATCHED_ACCOUNTS],
    ).save()

    async with World(WORKING_ACCOUNT.name) as world:
        await CreateWallet(
            app_state=world.app_state,
            beekeeper=world.beekeeper,
            wallet=WORKING_ACCOUNT.name,
            password=WORKING_ACCOUNT_PASSWORD,
        ).execute_with_result()

        await world.node.set_address(Url.parse(node.http_endpoint.as_string()))
        world.profile_data.working_account.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
        )
        await world.commands.sync_data_with_beekeeper()


@pytest.fixture()
async def cli_tester() -> CLITester:
    """Will return CliveTyper and CliRunner from typer.testing module.."""
    # import cli after default profile is set, default values for --profile-name option are set during loading
    from clive.__private.cli.main import cli

    env = {"COLUMNS": "100"}
    runner = CliRunner(env=env)

    return CLITester(cli, runner)
