from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import CLIChangingRecoveryAccountToWarningAccountError
from clive.__private.core.constants.alarms import WARNING_RECOVERY_ACCOUNTS
from clive.__private.models.schemas import ChangeRecoveryAccountOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.checkers import assert_no_pending_change_recovery_account
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


async def fetch_recovery_account(cli_tester: CLITester) -> str:
    world = cli_tester.world
    accounts = [world.profile.accounts.working.name]
    wrapper = (await world.commands.find_accounts(accounts=accounts)).result_or_raise
    return wrapper[0].recovery_account


async def test_change_recovery_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    new_recovery_account = WATCHED_ACCOUNTS_NAMES[0]
    operation = ChangeRecoveryAccountOperation(
        account_to_recover=WORKING_ACCOUNT_NAME,
        new_recovery_account=new_recovery_account,
    )

    # ACT
    result = cli_tester.process_change_recovery_account(new_recovery_account=new_recovery_account)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_cancel_change_recovery_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Operation with old recovery account cancels pending request."""
    # ARRANGE
    old_recovery_account = await fetch_recovery_account(cli_tester)
    new_recovery_account = WATCHED_ACCOUNTS_NAMES[0]
    cli_tester.configure_known_account_add(account_name=old_recovery_account)
    cli_tester.process_change_recovery_account(new_recovery_account=new_recovery_account)
    operation = ChangeRecoveryAccountOperation(
        account_to_recover=WORKING_ACCOUNT_NAME,
        new_recovery_account=old_recovery_account,
    )

    # ACT
    result = cli_tester.process_change_recovery_account(new_recovery_account=old_recovery_account)

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
    assert_no_pending_change_recovery_account(cli_tester)


@pytest.mark.parametrize("warning_account", WARNING_RECOVERY_ACCOUNTS)
async def test_negative_change_to_warning_account(cli_tester: CLITester, warning_account: str) -> None:
    # ACT & ASSERT
    with pytest.raises(
        CLITestCommandError,
        match=get_formatted_error_message(CLIChangingRecoveryAccountToWarningAccountError(warning_account)),
    ):
        cli_tester.process_change_recovery_account(new_recovery_account=warning_account)
