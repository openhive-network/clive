from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS
from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.core.world import World
from clive.__private.settings import settings
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA, run_node

if TYPE_CHECKING:
    import test_tools as tt


@pytest.fixture
async def prepare_profile() -> Profile:
    profile = Profile.create(
        WORKING_ACCOUNT_DATA.account.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
        watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
    )
    profile.save()
    return profile


@pytest.fixture
async def world(prepare_profile: Profile) -> World:  # noqa: ARG001
    return World()  # will load last profile by default


@pytest.fixture
async def prepare_beekeeper_wallet(world: World) -> None:
    async with world as world_cm:
        await world_cm.commands.create_wallet(password=WORKING_ACCOUNT_PASSWORD)

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
async def cli_tester(node: tt.RawNode, prepare_beekeeper_wallet: None) -> CLITester:  # noqa: ARG001
    """Will return CliveTyper and CliRunner from typer.testing module.."""
    # import cli after default profile is set, default values for --profile-name option are set during loading
    from clive.__private.cli.main import cli

    env = {"COLUMNS": f"{TERMINAL_WIDTH}"}
    runner = CliRunner(env=env)
    return CLITester(cli, runner)
