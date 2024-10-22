from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.create_profile_encryption_wallet import CreateProfileEncryptionWallet
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.lock import Lock
from clive.__private.core.commands.unlock import Unlock
from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS
from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.core.world import World
from clive.__private.settings import settings
from clive.__private.storage.service import PersistentStorageService
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.data.constants import (
    BEEKEEPER_REMOTE_ADDRESS_ENV_NAME,
    BEEKEEPER_SESSION_TOKEN_ENV_NAME,
    NODE_CHAIN_ID_ENV_NAME,
    TESTNET_CHAIN_ID,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import (
    run_node,
)

if TYPE_CHECKING:
    import test_tools as tt


@pytest.fixture
async def node() -> tt.RawNode:
    node = run_node()
    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())
    return node


@pytest.fixture
async def cli_tester(
    node: tt.RawNode,  # noqa: ARG001
    beekeeper: Beekeeper,  # noqa: ARG001
    prepare_profile: Profile,  # noqa: ARG001
    prepare_wallet: None,  # noqa: ARG001
) -> CLITester:
    """Will return CliveTyper and CliRunner from typer.testing module, beekeeper is unlocked."""
    # import cli after profile is set prepared, default values for options are set during loading
    from clive.__private.cli.main import cli

    env = {"COLUMNS": f"{TERMINAL_WIDTH}"}
    runner = CliRunner(env=env)
    return CLITester(cli, runner)


@pytest.fixture
async def cli_tester_with_session_token_locked(
    cli_tester: CLITester,
    beekeeper: Beekeeper,
    prepare_profile: Profile,
) -> CLITester:
    """Will return CliveTyper and CliRunner from typer.testing module, beekeeper is locked."""
    wallet_name = prepare_profile.name
    await Lock(beekeeper=beekeeper, wallet=wallet_name).execute()
    return cli_tester
