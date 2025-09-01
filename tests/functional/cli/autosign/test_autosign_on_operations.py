from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.exceptions import (
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
    assert_no_exit_code_error,
    assert_transaction_file_is_signed,
    assert_transaction_file_is_unsigned,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-autosign-single-key"
ADDITIONAL_KEY_VALUE: str = PrivateKey.create().value
ADDITIONAL_KEY_ALIAS_NAME: Final[str] = f"{WORKING_ACCOUNT_KEY_ALIAS}_2"


async def test_autosign_when_there_is_no_sign_with(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    )

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_autosign_failure_due_to_no_keys_in_profile(
    cli_tester: CLITester,
) -> None:
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
        )


async def test_autosign_failure_due_to_multiple_keys_in_profile(
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIMultipleKeysAutoSignError())):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            memo=MEMO,
        )


async def test_default_autosigning_operation(cli_tester: CLITester, tmp_path: Path) -> None:
    # ARRANGE
    signed_transaction_file = tmp_path / "signed_transaction.txt"

    # ACT
    cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        memo=MEMO,
        broadcast=False,
        save_file=signed_transaction_file,
    )

    # ASSERT
    assert_transaction_file_is_signed(signed_transaction_file)


async def test_usage_of_autosign_with_sign_with(
    cli_tester: CLITester,
) -> None:
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


@pytest.mark.parametrize("autosign", [True, False])
async def test_saving_autosigned_operation_to_file(
    cli_tester: CLITester,
    tmp_path: Path,
    *,
    autosign: bool,
) -> None:
    # ARRANGE
    save_file = tmp_path / "saved_transaction.txt"

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        memo=MEMO,
        save_file=save_file,
        broadcast=False,
        autosign=autosign,
    )

    # ASSERT
    assert_no_exit_code_error(result)
    if autosign:
        assert_transaction_file_is_signed(save_file)
    else:
        assert_transaction_file_is_unsigned(save_file)


async def test_dry_run_of_not_autosigned_operation_on_profile_without_keys(
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    for alias in cli_tester.world.profile.keys.get_all_aliases():
        cli_tester.configure_key_remove(alias=alias)

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, autosign=False, broadcast=False
    )

    # ASSERT
    assert_contains_dry_run_message(result.stdout)


async def test_dry_run_of_not_autosigned_operation_on_profile_with_multiple_keys(
    cli_tester: CLITester,
) -> None:
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), to=RECEIVER, autosign=False, broadcast=False
    )

    # ASSERT
    assert_contains_dry_run_message(result.stdout)


async def test_saving_not_autosigned_operation_on_profile_without_keys(
    cli_tester: CLITester,
    tmp_path: Path,
) -> None:
    # ARRANGE
    save_file = tmp_path / "saved_transaction.txt"
    aliases = cli_tester.world.profile.keys.get_all_aliases()
    for alias in aliases:
        cli_tester.configure_key_remove(alias=alias)

    # ACT
    cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        autosign=False,
        broadcast=False,
        save_file=save_file,
    )

    # ASSERT
    assert_transaction_file_is_unsigned(save_file)


async def test_saving_not_autosigned_operation_on_profile_with_multiple_keys(
    cli_tester: CLITester,
    tmp_path: Path,
) -> None:
    # ARRANGE
    save_file = tmp_path / "saved_transaction.txt"
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT
    cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        autosign=False,
        broadcast=False,
        save_file=save_file,
    )

    # ASSERT
    assert_transaction_file_is_unsigned(save_file)
