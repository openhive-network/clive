from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.core.world import World
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA, run_node

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    import test_tools as tt

    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive_local_tools.types import EnvContextFactory


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
async def world(prepare_profile: Profile) -> World:
    return World(profile_name=prepare_profile.name)


@pytest.fixture
async def prepare_beekeeper_wallet(world: World) -> AsyncGenerator[World]:
    """Prepare wallet and yield World inside of context manager ready to use."""
    async with world as world_cm:
        await world_cm.commands.create_wallet(password=WORKING_ACCOUNT_PASSWORD)

        world_cm.profile.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}")
        )
        await world_cm.commands.sync_data_with_beekeeper()
        world_cm.profile.save()  # required for saving imported keys aliases
        yield world_cm


async def beekeeper(
    prepare_beekeeper_wallet: World, beekeeper_remote_address_env_context_factory: EnvContextFactory
) -> AsyncGenerator[Beekeeper]:
    address = str(prepare_beekeeper_wallet.beekeeper.http_endpoint)
    with beekeeper_remote_address_env_context_factory(address):
        yield prepare_beekeeper_wallet.beekeeper


@pytest.fixture
async def node(node_address_env_context_factory: EnvContextFactory) -> AsyncGenerator[tt.RawNode]:
    node = run_node()
    address = str(node.http_endpoint)
    with node_address_env_context_factory(address):
        yield node


@pytest.fixture
async def cli_tester(
    node: tt.RawNode,  # noqa: ARG001
    beekeeper: Beekeeper,
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    cli_tester_without_session_token: CLITester,
) -> AsyncGenerator[CLITester]:
    """Token is set in environment variable. Beekeeper session is unlocked."""
    with beekeeper_session_token_env_context_factory(beekeeper.token):
        yield cli_tester_without_session_token


@pytest.fixture
async def cli_tester_with_session_token_locked(
    beekeeper: Beekeeper,
    cli_tester: CLITester,
) -> CLITester:
    """Token is set in environment variable. Beekeeper session is locked."""
    await beekeeper.api.lock_all()
    return cli_tester


@pytest.fixture
async def cli_tester_without_session_token(
    beekeeper_session_token_env_context_factory: EnvContextFactory,
    cli_tester: CLITester,
) -> AsyncGenerator[CLITester]:
    """Token is not set in environment variable."""
    with beekeeper_session_token_env_context_factory(None):
        yield cli_tester
