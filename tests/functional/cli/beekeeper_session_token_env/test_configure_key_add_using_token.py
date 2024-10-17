from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.keys.keys import PrivateKey
from clive_local_tools.cli.exceptions import CLITestCommandError

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_configure_key_add_using_beekeeper_session_token(
    cli_tester: CLITester,
) -> None:
    """Add key using CLIVE_BEEKEEPER_SESSION_TOKEN."""
    # ARRANGE
    pk = PrivateKey.create()

    # ACT & ASSERT
    cli_tester.configure_key_add(key=pk.value, alias="add_key")


async def test_configure_key_add_with_beekeeper_session_token_not_unlocked(
    cli_tester_with_session_token_locked: CLITester,
) -> None:
    """Check if clive configure add_key command throws exception when wallet is not unlocked using session token."""
    # ARRANGE
    pk = PrivateKey.create()
    message = "There must be exactly one unlocked wallet with profile encryption key"

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester_with_session_token_locked.configure_key_add(key=pk.value, alias="add_key")
