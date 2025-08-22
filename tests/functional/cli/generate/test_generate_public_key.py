from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_generate_public_key_from_given_private_key(cli_tester_locked: CLITester) -> None:
    """Check clive generate public-key command."""
    # ACT
    result = cli_tester_locked.generate_public_key(password_stdin=WORKING_ACCOUNT_DATA.account.private_key)

    # ASSERT
    assert result.stdout.strip() == WORKING_ACCOUNT_DATA.account.public_key, "Public key should match private key."
