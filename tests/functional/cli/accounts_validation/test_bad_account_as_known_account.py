from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLITransactionBadAccountError
from clive.__private.core.accounts.account_manager import AccountManager
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

BAD_ACCOUNT: Final[str] = AccountManager.get_bad_accounts()[0]
EXPECTED_MESSAGE = get_formatted_error_message(CLITransactionBadAccountError(BAD_ACCOUNT))


async def test_bad_accounts_as_known_account(
    cli_tester: CLITester,
) -> None:
    """
    Bad account on list of known accounts.

    This test will verify, if it is possible to make transaction to bad account, event if this account
    is on known account list.
    """
    # ARRANGE
    cli_tester.world.profile.accounts.add_known_account(BAD_ACCOUNT)
    await cli_tester.world.commands.save_profile()

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=EXPECTED_MESSAGE):
        cli_tester.process_power_up(amount=tt.Asset.Hive(10), to=BAD_ACCOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
