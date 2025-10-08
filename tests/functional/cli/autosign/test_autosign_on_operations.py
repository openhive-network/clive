from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.exceptions import (
    CLIKeyAliasNotFoundError,
    CLIMultipleKeysAutoSignError,
    CLIMutuallyExclusiveOptionsError,
    CLINoKeysAvailableError,
)
from clive.__private.core.keys.keys import PrivateKey
from clive.__private.models.schemas import TransferOperation
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.cli.checkers import (
    assert_contains_dry_run_message,
    assert_contains_transaction_created_message,
    assert_contains_transaction_saved_to_file_message,
    assert_transaction_file_is_signed,
    assert_transaction_file_is_unsigned,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import create_transaction_filepath, get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-autosign-single-key"
ADDITIONAL_KEY_VALUE: str = PrivateKey.create().value
ADDITIONAL_KEY_ALIAS_NAME: Final[str] = f"{WORKING_ACCOUNT_KEY_ALIAS}_2"


async def test_broadcasting_autosign_operation(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test broadcasting autosigned operation."""
    # ARRANGE
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    )

    # ACT
    result = cli_tester.process_transfer(
        from_=operation.from_,
        amount=operation.amount,
        to=operation.to,
        memo=operation.memo,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


@pytest.mark.parametrize("broadcast", [None, True], ids=["default broadcast", "explicit broadcast"])
async def test_negative_autosign_failure_due_to_no_keys_in_profile(
    cli_tester: CLITester, *, broadcast: bool | None
) -> None:
    """Test autosigning failure when there are no keys available and try to send operation."""
    # ARRANGE
    for alias in cli_tester.world.profile.keys.get_all_aliases():
        cli_tester.configure_key_remove(alias=alias)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLINoKeysAvailableError())):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            memo=MEMO,
            broadcast=broadcast,
        )


@pytest.mark.parametrize("broadcast", [None, True], ids=["default broadcast", "explicit broadcast"])
async def test_negative_autosign_failure_due_to_multiple_keys_in_profile(
    cli_tester: CLITester, *, broadcast: bool | None
) -> None:
    """Test autosigning failure when there are multiple keys available and try to send operation."""
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIMultipleKeysAutoSignError())):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, memo=MEMO, broadcast=broadcast
        )


async def test_negative_usage_of_autosign_with_sign_with(cli_tester: CLITester) -> None:
    """Test failure of using both 'autosign' and 'sign_with' flags."""
    # ACT & ASSERT
    with pytest.raises(
        CLITestCommandError,
        match=get_formatted_error_message(CLIMutuallyExclusiveOptionsError("autosign", "sign-with")),
    ):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            memo=MEMO,
            autosign=True,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


@pytest.mark.parametrize(
    "autosign", [False, None, True], ids=["autosign disabled", "autosign by default", "autosign explicit"]
)
async def test_saving_autosigned_operation_to_file(cli_tester: CLITester, *, autosign: bool) -> None:
    """Test the effect of explicitly passing the 'autosign/no-autosign' flag when saving an operation to a file."""
    # ARRANGE
    transaction_filepath = create_transaction_filepath()

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        memo=MEMO,
        save_file=transaction_filepath,
        broadcast=False,
        autosign=autosign,
    )

    # ASSERT
    if autosign in [True, None]:
        assert_transaction_file_is_signed(transaction_filepath)
    else:
        assert_transaction_file_is_unsigned(transaction_filepath)
    assert_contains_dry_run_message(result.stdout)
    assert_contains_transaction_created_message(result.stdout)
    assert_contains_transaction_saved_to_file_message(transaction_filepath, result.stdout)


async def test_dry_run_of_not_autosigned_operation_on_profile_without_keys(cli_tester: CLITester) -> None:
    """
    Test printing out dry run and successful transaction creation messages.

    We should be able to print out a not autosigned transaction when there are no keys.
    """
    # ARRANGE
    for alias in cli_tester.world.profile.keys.get_all_aliases():
        cli_tester.configure_key_remove(alias=alias)

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, autosign=False, broadcast=False
    )

    # ASSERT
    assert_contains_dry_run_message(result.stdout)
    assert_contains_transaction_created_message(result.stdout)


async def test_dry_run_of_not_autosigned_operation_on_profile_with_multiple_keys(cli_tester: CLITester) -> None:
    """
    Test printing out dry run and successful transaction creation messages.

    We should be able to print out a not autosigned transaction when there are multiple keys.
    """
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, autosign=False, broadcast=False
    )

    # ASSERT
    assert_contains_dry_run_message(result.stdout)
    assert_contains_transaction_created_message(result.stdout)


@pytest.mark.parametrize("autosign", [None, True])
async def test_negative_dry_run_of_autosigned_operation_on_profile_without_keys(
    cli_tester: CLITester,
    *,
    autosign: bool | None,
) -> None:
    """
    Test failing of printing out dry run and transaction.

    It should fail when we try to print out an autosigned transaction when there are no keys.
    """
    for alias in cli_tester.world.profile.keys.get_all_aliases():
        cli_tester.configure_key_remove(alias=alias)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLINoKeysAvailableError())):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, autosign=autosign, broadcast=False
        )


@pytest.mark.parametrize("autosign", [None, True])
async def test_negative_dry_run_of_autosigned_operation_on_profile_with_multiple_keys(
    cli_tester: CLITester,
    *,
    autosign: bool | None,
) -> None:
    """
    Test failing of printing out dry run and transaction.

    It should fail when we try to print out an autosigned transaction when there are multiple keys.
    """
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIMultipleKeysAutoSignError())):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, autosign=autosign, broadcast=False
        )


async def test_saving_not_autosigned_operation_on_profile_without_keys(cli_tester: CLITester) -> None:
    """
    Test saving transaction to the file.

    We should be able to save not autosigned transaction when there are no keys.
    """
    # ARRANGE
    transaction_filepath = create_transaction_filepath()

    aliases = cli_tester.world.profile.keys.get_all_aliases()
    for alias in aliases:
        cli_tester.configure_key_remove(alias=alias)

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        autosign=False,
        broadcast=False,
        save_file=transaction_filepath,
    )

    # ASSERT
    assert_transaction_file_is_unsigned(transaction_filepath)
    assert_contains_transaction_saved_to_file_message(transaction_filepath, result.stdout)


async def test_saving_not_autosigned_operation_on_profile_with_multiple_keys(cli_tester: CLITester) -> None:
    """
    Test saving transaction to the file.

    We should be able to save not autosigned transaction when there are multiple keys.
    """
    # ARRANGE
    transaction_filepath = create_transaction_filepath()
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        autosign=False,
        broadcast=False,
        save_file=transaction_filepath,
    )

    # ASSERT
    assert_transaction_file_is_unsigned(transaction_filepath)
    assert_contains_transaction_saved_to_file_message(transaction_filepath, result.stdout)


async def test_negative_sign_with_takes_precedence_over_autosign(cli_tester: CLITester) -> None:
    """Test that using sign_with takes precedence over the default autosign."""
    # ARRANGE
    sign_with = "non-existing"

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIKeyAliasNotFoundError(sign_with))):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME, amount=AMOUNT, to=RECEIVER, memo=MEMO, sign_with=sign_with
        )
