from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.error_handlers.communication_failure_notificator import CommunicationFailureNotificator
from clive.__private.models.schemas import TransferToSavingsOperation
from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_operation_from_transaction, get_transaction_id_from_output
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_DEPOSIT_HBD: Final[tt.Asset.HbdT] = tt.Asset.Hbd(0.237)
AMOUNT_TO_DEPOSIT_HIVE: Final[tt.Asset.HiveT] = tt.Asset.Test(0.235)
LARGE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(234234.235)
DEPOSIT_MEMO: Final[str] = "memo0"


@pytest.mark.parametrize(
    ("amount_to_deposit", "working_account_balance"),
    [
        (AMOUNT_TO_DEPOSIT_HIVE, WORKING_ACCOUNT_DATA.hives_liquid),
        (AMOUNT_TO_DEPOSIT_HBD, WORKING_ACCOUNT_DATA.hbds_liquid),
    ],
    ids=["hive", "hbd"],
)
async def test_deposit_valid(
    cli_tester: CLITester,
    amount_to_deposit: tt.Asset.AnyT,
    working_account_balance: tt.Asset.AnyT,
) -> None:
    # ACT
    cli_tester.process_savings_deposit(amount=amount_to_deposit, sign_with=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=amount_to_deposit,
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=working_account_balance - amount_to_deposit,
        balance="Liquid",
    )


async def test_deposit_to_other_account(cli_tester: CLITester) -> None:
    # ARRANGE
    other_account_data = WATCHED_ACCOUNTS_DATA[0]
    other_account = other_account_data.account

    # ACT
    cli_tester.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT_HIVE,
        to=other_account.name,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        from_=WORKING_ACCOUNT_DATA.account.name,
    )

    # ASSERT
    checkers.assert_balances(
        cli_tester,
        account_name=other_account.name,
        asset_amount=AMOUNT_TO_DEPOSIT_HIVE,
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT_TO_DEPOSIT_HIVE,
        balance="Liquid",
    )


async def test_deposit_not_enough_hive(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = CommunicationFailureNotificator.YOU_DONT_HAVE_ENOUGH_FUNDS_MESSAGE

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as deposit_exception_info:
        cli_tester.process_savings_deposit(amount=LARGE_AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
    checkers.assert_exit_code(deposit_exception_info, 1)

    # ASSERT
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=tt.Asset.Hive(0),
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=WORKING_ACCOUNT_DATA.hives_liquid,
        balance="Liquid",
    )


async def test_deposit_with_memo(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_savings_deposit(
        amount=AMOUNT_TO_DEPOSIT_HIVE,
        memo=DEPOSIT_MEMO,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert DEPOSIT_MEMO in result.output, f"There should be memo `{DEPOSIT_MEMO}` in transaction."
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=AMOUNT_TO_DEPOSIT_HIVE,
        balance="Savings",
    )
    checkers.assert_balances(
        cli_tester,
        account_name=WORKING_ACCOUNT_DATA.account.name,
        asset_amount=WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT_TO_DEPOSIT_HIVE,
        balance="Liquid",
    )


async def test_deposit_with_encrypted_memo(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check that savings deposit encrypts memo when it starts with '#'."""
    # ARRANGE
    memo_content = "#This is a secret savings deposit memo"

    # ACT
    result = cli_tester.process_savings_deposit(
        from_=WORKING_ACCOUNT_DATA.account.name,
        to=WORKING_ACCOUNT_DATA.account.name,
        amount=AMOUNT_TO_DEPOSIT_HIVE,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=memo_content,
    )

    # ASSERT
    assert result.exit_code == 0

    transaction_id = get_transaction_id_from_output(result.stdout)
    op = get_operation_from_transaction(node, transaction_id, TransferToSavingsOperation)
    assert op.memo.startswith("#"), "Encrypted memos start with '#' followed by the encoded key data"
    assert len(op.memo) > len(memo_content), "The encrypted memo should be longer than the original"
