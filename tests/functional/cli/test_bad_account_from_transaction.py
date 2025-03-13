from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLITransactionBadAccountError
from clive.__private.core.accounts.account_manager import _load_bad_accounts_from_file
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.fixture
def first_of_bad_accounts() -> str:
    """Return first account of bad accounts, iterating over all accounts would be time consuming."""
    return _load_bad_accounts_from_file()[0]


@pytest.mark.parametrize("amount", [tt.Asset.Vest(5000.000), tt.Asset.Hive(10.000)])
async def test_bad_accounts_delegate_vesting_shares_set(
    cli_tester: CLITester,
    amount: tt.Asset.VestT | tt.Asset.HiveT,
    first_of_bad_accounts: str,
) -> None:
    # ARRANGE
    message = CLITransactionBadAccountError(first_of_bad_accounts).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_delegations_set(
            delegatee=first_of_bad_accounts, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS
        )


async def test_bad_accounts_set_withdraw_vesting_route_set(
    cli_tester: CLITester,
    first_of_bad_accounts: str,
) -> None:
    # ARRANGE
    percent: int = 30
    message = CLITransactionBadAccountError(first_of_bad_accounts).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_withdraw_routes_set(
            to=first_of_bad_accounts, percent=percent, sign=WORKING_ACCOUNT_KEY_ALIAS
        )


@pytest.mark.parametrize("amount", [tt.Asset.Hbd(10.000), tt.Asset.Hive(10.000)])
async def test_bad_accounts_transfer_from_savings(
    cli_tester: CLITester,
    amount: tt.Asset.HbdT | tt.Asset.HiveT,
    first_of_bad_accounts: str,
) -> None:
    # ARRANGE
    message = CLITransactionBadAccountError(first_of_bad_accounts).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_savings_withdrawal(to=first_of_bad_accounts, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS)


@pytest.mark.parametrize("amount", [tt.Asset.Hbd(10.000), tt.Asset.Hive(10.000)])
async def test_bad_accounts_transfer_to_savings(
    cli_tester: CLITester,
    amount: tt.Asset.HbdT | tt.Asset.HiveT,
    first_of_bad_accounts: str,
) -> None:
    # ARRANGE
    message = CLITransactionBadAccountError(first_of_bad_accounts).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_savings_deposit(to=first_of_bad_accounts, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS)


async def test_bad_accounts_transfer_to_vesting(
    cli_tester: CLITester,
    first_of_bad_accounts: str,
) -> None:
    # ARRANGE
    amount: tt.Asset.HiveT = tt.Asset.Hive(10.000)
    message = CLITransactionBadAccountError(first_of_bad_accounts).message

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_power_up(amount=amount, to=first_of_bad_accounts, sign=WORKING_ACCOUNT_KEY_ALIAS)
