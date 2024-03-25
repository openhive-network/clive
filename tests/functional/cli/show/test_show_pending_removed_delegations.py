from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive_local_tools.cli import checkers
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS[0]


async def test_removed_delegations_none(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_pending_removed_delegations()

    # ASSERT
    assert "no removed delegations" in result.stdout
