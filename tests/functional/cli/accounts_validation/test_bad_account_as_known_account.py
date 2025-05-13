from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLITransactionBadAccountError
from clive.__private.core.accounts.account_manager import AccountManager
from clive_local_tools.cli.checkers import assert_output_contains
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
    cli_tester.configure_known_account_add(account_name=BAD_ACCOUNT)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError) as error:
        cli_tester.process_power_up(amount=tt.Asset.Hive(10), to=BAD_ACCOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS)
    assert_output_contains(EXPECTED_MESSAGE, error.value.stdout)
