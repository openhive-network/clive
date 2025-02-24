from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLITransactionUnknownAccountError
from clive.__private.models.schemas import AccountName
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

UNKNOWN_ACCOUNT: Final[AccountName] = AccountName("abrakadabra")


@pytest.mark.parametrize("amount", [tt.Asset.Vest(5000.000), tt.Asset.Hive(10.000)])
async def test_unknown_accounts_delegate_vesting_shares_set(
    cli_tester: CLITester, amount: tt.Asset.VestT | tt.Asset.HiveT
) -> None:
    # ARRANGE
    message = CLITransactionUnknownAccountError(UNKNOWN_ACCOUNT).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_delegations_set(delegatee=UNKNOWN_ACCOUNT, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS)


@pytest.mark.parametrize("amount", [tt.Asset.Vest(5000.000), tt.Asset.Hive(10.000)])
async def test_unknown_accounts_delegate_vesting_shares_remove(
    cli_tester: CLITester, amount: tt.Asset.VestT | tt.Asset.HiveT
) -> None:
    # ARRANGE
    message = CLITransactionUnknownAccountError(ALT_WORKING_ACCOUNT1_NAME).message
    cli_tester.configure_known_account_add(account_name=ALT_WORKING_ACCOUNT1_NAME)
    cli_tester.process_delegations_set(
        delegatee=ALT_WORKING_ACCOUNT1_NAME, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS
    )
    cli_tester.configure_known_account_remove(account_name=ALT_WORKING_ACCOUNT1_NAME)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_delegations_remove(delegatee=ALT_WORKING_ACCOUNT1_NAME, sign=WORKING_ACCOUNT_KEY_ALIAS)


async def test_unknown_accounts_set_withdraw_vesting_route_set(
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    percent: int = 30
    message = CLITransactionUnknownAccountError(UNKNOWN_ACCOUNT).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_withdraw_routes_set(to=UNKNOWN_ACCOUNT, percent=percent, sign=WORKING_ACCOUNT_KEY_ALIAS)


async def test_unknown_accounts_set_withdraw_vesting_route_remove(
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    percent: int = 30
    message = CLITransactionUnknownAccountError(ALT_WORKING_ACCOUNT1_NAME).message
    cli_tester.configure_known_account_add(account_name=ALT_WORKING_ACCOUNT1_NAME)
    cli_tester.process_withdraw_routes_set(
        to=ALT_WORKING_ACCOUNT1_NAME, percent=percent, sign=WORKING_ACCOUNT_KEY_ALIAS
    )
    cli_tester.configure_known_account_remove(account_name=ALT_WORKING_ACCOUNT1_NAME)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_withdraw_routes_remove(to=ALT_WORKING_ACCOUNT1_NAME, sign=WORKING_ACCOUNT_KEY_ALIAS)


@pytest.mark.parametrize("amount", [tt.Asset.Hbd(10.000), tt.Asset.Hive(10.000)])
async def test_unknown_accounts_transfer_from_savings(
    cli_tester: CLITester, amount: tt.Asset.HbdT | tt.Asset.HiveT
) -> None:
    # ARRANGE
    message = CLITransactionUnknownAccountError(UNKNOWN_ACCOUNT).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_savings_withdrawal(to=UNKNOWN_ACCOUNT, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS)


@pytest.mark.parametrize("amount", [tt.Asset.Hbd(10.000), tt.Asset.Hive(10.000)])
async def test_unknown_accounts_transfer_from_savings_cancel(
    cli_tester: CLITester, amount: tt.Asset.HbdT | tt.Asset.HiveT
) -> None:
    # ARRANGE
    request_id: int = 13
    message = CLITransactionUnknownAccountError(ALT_WORKING_ACCOUNT1_NAME).message
    cli_tester.configure_known_account_add(account_name=ALT_WORKING_ACCOUNT1_NAME)
    cli_tester.process_savings_withdrawal(
        to=ALT_WORKING_ACCOUNT1_NAME, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id
    )
    cli_tester.configure_known_account_remove(account_name=ALT_WORKING_ACCOUNT1_NAME)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_savings_withdrawal_cancel(
            from_=ALT_WORKING_ACCOUNT1_NAME, sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id
        )


@pytest.mark.parametrize("amount", [tt.Asset.Hbd(10.000), tt.Asset.Hive(10.000)])
async def test_unknown_accounts_transfer_to_savings(
    cli_tester: CLITester, amount: tt.Asset.HbdT | tt.Asset.HiveT
) -> None:
    # ARRANGE
    message = CLITransactionUnknownAccountError(UNKNOWN_ACCOUNT).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_savings_deposit(to=UNKNOWN_ACCOUNT, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS)


async def test_unknown_accounts_transfer_to_vesting(cli_tester: CLITester) -> None:
    # ARRANGE
    amount: tt.Asset.HiveT = tt.Asset.Hive(10.000)
    message = CLITransactionUnknownAccountError(UNKNOWN_ACCOUNT).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_power_up(amount=amount, to=UNKNOWN_ACCOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS)
