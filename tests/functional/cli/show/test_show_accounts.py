from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_show_accounts(cli_tester: CLITester) -> None:
    """Check clive show accounts command."""
    # ACT & ASSERT
    cli_tester.show_accounts()
