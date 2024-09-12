from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.keys.keys import PrivateKey
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import BEEKEEPER_SESSION_TOKEN_ENV_NAME, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.types import CLITesterWithSessionT


async def test_add_key_using_beekeeper_session_token(
    cli_tester_with_session_token_unlocked: CLITester,
) -> None:
    """Add key using CLIVE_BEEKEEPER_SESSION_TOKEN."""
    # ARRANGE
    pk = PrivateKey.create()

    # ACT & ASSERT
    cli_tester_with_session_token_unlocked.configure_key_add(key=pk.value, alias="add_key")


@pytest.mark.parametrize("unlocked", [True, False])
async def test_add_key_with_beekeeper_session_token_and_password_both_set_with_different_wallet_state(
    cli_tester_with_session: CLITesterWithSessionT, *, unlocked: bool
) -> None:
    """
    Check clive configure key add command.

    If it throws exception when there is password and session token set while wallet is locked/unlocked.
    """
    # ARRANGE
    cli_tester = cli_tester_with_session(unlocked=unlocked)
    pk = PrivateKey.create()
    message = (
        f"Both '--password' flag and environment variable {BEEKEEPER_SESSION_TOKEN_ENV_NAME} are set."
        " Please use only one."
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.configure_key_add(key=pk.value, alias="add_key", password=WORKING_ACCOUNT_PASSWORD)


async def test_add_key_with_beekeeper_session_token_not_unlocked(
    cli_tester_with_session_token_locked: CLITester,
) -> None:
    """Check if clive configure add_key command throws exception when wallet is not unlocked using session token."""
    # ARRANGE
    pk = PrivateKey.create()
    message = (
        f"If you want to use {BEEKEEPER_SESSION_TOKEN_ENV_NAME} envvar,"
        f" ensure it is in unlocked state for wallet {WORKING_ACCOUNT_NAME}."
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.configure_key_add(key=pk.value, alias="add_key")
