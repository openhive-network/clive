from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.models.schemas import AccountName
from clive_local_tools.checkers.profile_accounts_checker import ProfileAccountsChecker
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_NAME, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

UNKNOWN_ACCOUNT: Final[AccountName] = AccountName(ALT_WORKING_ACCOUNT1_NAME)


@pytest.fixture
async def cli_tester_disabled_known_accounts(cli_tester: CLITester) -> CLITester:
    cli_tester.configure_known_account_disable()
    profile_checker = ProfileAccountsChecker(cli_tester.world.profile.name, cli_tester.world.beekeeper_manager._content)
    await profile_checker.assert_not_in_known_accounts(account_names=[UNKNOWN_ACCOUNT])
    return cli_tester


@pytest.mark.parametrize("amount", [tt.Asset.Vest(5000.000), tt.Asset.Hive(10.000)])
async def test_disabled_known_accounts_delegate_vesting_shares_set(
    cli_tester_disabled_known_accounts: CLITester, amount: tt.Asset.VestT | tt.Asset.HiveT
) -> None:
    # ACT & ASSERT
    cli_tester_disabled_known_accounts.process_delegations_set(
        delegatee=UNKNOWN_ACCOUNT, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


@pytest.mark.parametrize("amount", [tt.Asset.Vest(5000.000), tt.Asset.Hive(10.000)])
async def test_disabled_known_accounts_delegate_vesting_shares_remove(
    cli_tester_disabled_known_accounts: CLITester, amount: tt.Asset.VestT | tt.Asset.HiveT
) -> None:
    # ACT
    cli_tester_disabled_known_accounts.process_delegations_set(
        delegatee=UNKNOWN_ACCOUNT, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    cli_tester_disabled_known_accounts.process_delegations_remove(
        delegatee=UNKNOWN_ACCOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_disabled_known_accounts_set_withdraw_vesting_route_set(
    cli_tester_disabled_known_accounts: CLITester,
) -> None:
    # ARRANGE
    percent: int = 30

    # ACT & ASSERT
    cli_tester_disabled_known_accounts.process_withdraw_routes_set(
        to=UNKNOWN_ACCOUNT, percent=percent, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


@pytest.mark.parametrize("amount", [tt.Asset.Hbd(10.000), tt.Asset.Hive(10.000)])
async def test_disabled_known_accounts_transfer_from_savings(
    cli_tester_disabled_known_accounts: CLITester, amount: tt.Asset.HbdT | tt.Asset.HiveT
) -> None:
    # ACT & ASSERT
    cli_tester_disabled_known_accounts.process_savings_withdrawal(
        to=UNKNOWN_ACCOUNT, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


@pytest.mark.parametrize("amount", [tt.Asset.Hbd(10.000), tt.Asset.Hive(10.000)])
async def test_disabled_known_accounts_transfer_from_savings_cancel(
    cli_tester_disabled_known_accounts: CLITester, amount: tt.Asset.HbdT | tt.Asset.HiveT
) -> None:
    # ARRANGE
    request_id: int = 13

    # ACT
    cli_tester_disabled_known_accounts.process_savings_withdrawal(
        to=UNKNOWN_ACCOUNT, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id
    )

    # ASSERT
    cli_tester_disabled_known_accounts.process_savings_withdrawal_cancel(
        from_=WORKING_ACCOUNT_NAME, sign=WORKING_ACCOUNT_KEY_ALIAS, request_id=request_id
    )


@pytest.mark.parametrize("amount", [tt.Asset.Hbd(10.000), tt.Asset.Hive(10.000)])
async def test_disabled_known_accounts_transfer_to_savings(
    cli_tester_disabled_known_accounts: CLITester, amount: tt.Asset.HbdT | tt.Asset.HiveT
) -> None:
    # ACT & ASSERT
    cli_tester_disabled_known_accounts.process_savings_deposit(
        to=UNKNOWN_ACCOUNT, amount=amount, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_disabled_known_accounts_transfer_to_vesting(cli_tester_disabled_known_accounts: CLITester) -> None:
    # ARRANGE
    amount: tt.Asset.HiveT = tt.Asset.Hive(10.000)

    # ACT & ASSERT
    cli_tester_disabled_known_accounts.process_power_up(
        amount=amount, to=UNKNOWN_ACCOUNT, sign=WORKING_ACCOUNT_KEY_ALIAS
    )
