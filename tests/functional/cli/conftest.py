from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from clive.__private.core.commands.lock import Lock
from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS
from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.settings import settings
from clive_local_tools.cli.cli_tester import CLITester
from clive_local_tools.testnet_block_log import (
    run_node,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.profile import Profile
    from clive_local_tools.data.models import WalletInfo


@pytest.fixture
async def node() -> tt.RawNode:
    node = run_node()
    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())
    return node


@pytest.fixture
async def cli_tester(
    node: tt.RawNode,  # noqa: ARG001
    beekeeper: Beekeeper,  # noqa: ARG001
    prepare_profile_with_session: Profile,  # noqa: ARG001
    prepare_beekeeper_wallet_with_session: WalletInfo,  # noqa: ARG001
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
    prepare_profile_with_session: Profile,
) -> CLITester:
    """Will return CliveTyper and CliRunner from typer.testing module, beekeeper is locked."""
    wallet_name = prepare_profile_with_session.name
    await Lock(beekeeper=beekeeper, wallet=wallet_name).execute()
    return cli_tester
