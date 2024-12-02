from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.keys.keys import PrivateKey
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import BEEKEEPER_SESSION_TOKEN_ENV_NAME
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_configure_key_add_using_beekeeper_session_token(
    cli_tester_with_session_token_unlocked: CLITester,
) -> None:
    """Add key using CLIVE_BEEKEEPER__SESSION_TOKEN."""
    # ARRANGE
    pk = PrivateKey.create()

    # ACT & ASSERT
    cli_tester_with_session_token_unlocked.configure_key_add(key=pk.value, alias="add_key")


async def test_configure_key_add_with_beekeeper_session_token_not_unlocked(
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
