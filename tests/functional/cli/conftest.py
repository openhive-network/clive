from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS
from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.settings import settings
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    BEEKEEPER_REMOTE_ADDRESS_ENV_NAME,
    BEEKEEPER_SESSION_TOKEN_ENV_NAME,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    run_node,
)

if TYPE_CHECKING:
    from typing import AsyncIterator

    import test_tools as tt

    from clive.__private.core.profile import Profile
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
async def prepare_profile_and_wallet(beekeeper_remote: Beekeeper) -> Profile:
    async with World(
        profile_name=WORKING_ACCOUNT_DATA.account.name, beekeeper_remote_endpoint=beekeeper_remote.http_endpoint
    ) as world_cm:
        profile = world_cm.profile
        profile.accounts.set_working_account(WORKING_ACCOUNT_DATA.account.name)
        profile.accounts.watched.add(*WATCHED_ACCOUNTS_NAMES)
        await world_cm.commands.create_profile_encryption_key(password=WORKING_ACCOUNT_PASSWORD)
        await world_cm.commands.create_wallet(password=WORKING_ACCOUNT_PASSWORD)
        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
        )
        await world_cm.commands.sync_data_with_beekeeper()
    return profile


@pytest.fixture
async def node() -> tt.RawNode:
    node = run_node()
    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())
    return node


@pytest.fixture
async def cli_tester(
    node: tt.RawNode,  # noqa: ARG001
    prepare_profile_and_wallet: Profile,  # noqa: ARG001
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
