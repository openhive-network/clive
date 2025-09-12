from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive_local_tools.cli.checkers import assert_no_exit_code_error
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.mark.parametrize(
    "cli_tester_variant",
    [
        "unlocked",
        "locked",
        "without remote address",
        "without session token",
    ],
    indirect=True,
)
async def test_command_is_working_in_environment(cli_tester_variant: CLITester) -> None:
    # ACT
    result = cli_tester_variant.generate_public_key(password_stdin=WORKING_ACCOUNT_DATA.account.private_key)

    # ASSERT
    assert_no_exit_code_error(result)


async def test_generate_public_key_from_given_private_key(cli_tester_locked: CLITester) -> None:
    """Check clive generate public-key command."""
    # ACT
    result = cli_tester_locked.generate_public_key(password_stdin=WORKING_ACCOUNT_DATA.account.private_key)

    # ASSERT
    assert result.stdout.strip() == WORKING_ACCOUNT_DATA.account.public_key, "Public key should match private key."
