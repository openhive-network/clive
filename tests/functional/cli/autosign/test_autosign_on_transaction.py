from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import (
    CLIMultipleKeysAutoSignError,
    CLIMutuallyExclusiveOptionsError,
    CLINoKeysAvailableError,
    CLIWrongAlreadySignedModeAutoSignError,
)
from clive.__private.core.keys.keys import PrivateKey
from clive.__private.models.schemas import TransferOperation
from clive_local_tools.cli.checkers import (
    assert_contains_dry_run_message,
    assert_contains_transaction_broadcasted_message,
    assert_contains_transaction_loaded_message,
    assert_contains_transaction_saved_to_file_message,
    assert_output_contains,
    assert_transaction_file_is_signed,
    assert_transaction_file_is_unsigned,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import create_transaction_file, create_transaction_filepath, get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.types import AlreadySignedMode
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(10)
TO_ACCOUNT: Final[str] = WATCHED_ACCOUNTS_NAMES[0]
AUTO_SIGN_SKIPPED_WARNING_MESSAGE: Final[str] = "Your transaction is already signed. Autosign will be skipped"
ADDITIONAL_KEY_VALUE: str = PrivateKey.create().value
ADDITIONAL_KEY_ALIAS_NAME: Final[str] = f"{WORKING_ACCOUNT_KEY_ALIAS}_2"
WORKING_ACCOUNT_KEY_VALUE: str = WORKING_ACCOUNT_DATA.account.private_key


@pytest.fixture
def transaction_file_with_transfer() -> Path:
    operation = TransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=TO_ACCOUNT,
        amount=tt.Asset.Hive(10),
        memo="known account test",
    )

    return create_transaction_file(operation, "with_transfer")


@pytest.fixture
def signed_transaction_file_with_transfer(cli_tester: CLITester, transaction_file_with_transfer: Path) -> Path:
    transaction_file_path = create_transaction_filepath("signed_with_transfer")
    cli_tester.process_transaction(
        from_file=transaction_file_with_transfer, save_file=transaction_file_path, broadcast=False
    )
    return transaction_file_path


def assert_auto_sign_skipped_warning_message_in_output(output: str) -> None:
    assert_output_contains(AUTO_SIGN_SKIPPED_WARNING_MESSAGE, output)


async def test_autosign_transaction(cli_tester: CLITester, transaction_file_with_transfer: Path) -> None:
    """Test autosigning transaction."""
    # ARRANGE
    signed_transaction_filepath = create_transaction_filepath("signed")

    # ACT
    result = cli_tester.process_transaction(
        from_file=transaction_file_with_transfer, save_file=signed_transaction_filepath
    )

    # ASSERT
    assert_contains_transaction_saved_to_file_message(signed_transaction_filepath, result.stdout)
    assert_transaction_file_is_signed(signed_transaction_filepath)


async def test_autosign_transaction_with_different_aliases_to_the_same_key(
    cli_tester: CLITester,
    transaction_file_with_transfer: Path,
) -> None:
    """Test autosigning transaction when there are different aliases to the same key in the profile."""
    # ARRANGE
    signed_transaction_filepath = create_transaction_filepath("signed")
    cli_tester.configure_key_add(key=WORKING_ACCOUNT_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT
    result = cli_tester.process_transaction(
        from_file=transaction_file_with_transfer, save_file=signed_transaction_filepath
    )

    # ASSERT
    assert_contains_transaction_saved_to_file_message(signed_transaction_filepath, result.stdout)
    assert_transaction_file_is_signed(signed_transaction_filepath)


# If there will be other tests with various combinations of broadcast, save_to_file and autosign
# we can move this to a fixture in conftest.py as we did:
# tests/functional/cli/accounts_validation/conftest.py - process_action_selector
@pytest.mark.parametrize(
    ("broadcast", "save_to_file", "autosign"),
    [
        (True, True, True),
        (True, False, True),
        (False, True, True),
        (False, False, True),
        (True, True, None),
        (True, False, None),
        (False, True, None),
        (False, False, None),
    ],
    ids=[
        "broadcast and save_to_file, explicit autosign",
        "broadcast, explicit autosign",
        "save_to_file, explicit autosign",
        "show, explicit autosign",
        "broadcast and save_to_file",
        "broadcast",
        "save_to_file,",
        "show",
    ],
)
async def test_autosign_is_skipped_with_warning(
    cli_tester: CLITester,
    signed_transaction_file_with_transfer: Path,
    *,
    broadcast: bool,
    save_to_file: bool,
    autosign: bool | None,
) -> None:
    """
    Test skipping autosigning an already signed transaction.

    We should only display warning info about skipping autosigning.
    """
    # ARRANGE
    resaved_transaction_filepath = create_transaction_filepath("resaved") if save_to_file else None

    # ACT
    result = cli_tester.process_transaction(
        from_file=signed_transaction_file_with_transfer,
        broadcast=broadcast,
        save_file=resaved_transaction_filepath,
        autosign=autosign,
    )

    # ASSERT
    assert_auto_sign_skipped_warning_message_in_output(result.stdout)
    if not broadcast:
        assert_contains_transaction_loaded_message(result.stdout)
    else:
        assert_contains_transaction_broadcasted_message(result.stdout)
    if resaved_transaction_filepath:
        assert_contains_transaction_saved_to_file_message(resaved_transaction_filepath, result.stdout)


async def test_dry_run_autosign_is_skipped_with_warning_with_no_keys_in_profile(
    cli_tester: CLITester,
    signed_transaction_file_with_transfer: Path,
) -> None:
    """
    Test skipping autosigning an already signed transaction.

    We should only display warning info about skipping autosigning, even when there are no keys.
    """
    # ARRANGE
    for alias in cli_tester.world.profile.keys.get_all_aliases():
        cli_tester.configure_key_remove(alias=alias)

    # ACT
    result = cli_tester.process_transaction(from_file=signed_transaction_file_with_transfer, broadcast=False)

    # ASSERT
    assert_auto_sign_skipped_warning_message_in_output(result.stdout)
    assert_contains_transaction_loaded_message(result.stdout)
    assert_contains_dry_run_message(result.stdout)


async def test_dry_run_autosign_is_skipped_with_warning_with_multiple_keys_in_profile(
    cli_tester: CLITester,
    signed_transaction_file_with_transfer: Path,
) -> None:
    """
    Test skipping autosigning an already signed transaction.

    We should only display warning info about skipping autosigning, even when there are multiple keys.
    """
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT
    result = cli_tester.process_transaction(from_file=signed_transaction_file_with_transfer, broadcast=False)

    # ASSERT
    assert_auto_sign_skipped_warning_message_in_output(result.stdout)
    assert_contains_transaction_loaded_message(result.stdout)
    assert_contains_dry_run_message(result.stdout)


async def test_negative_autosign_transaction_failure_due_to_no_keys_in_profile(
    cli_tester: CLITester,
    transaction_file_with_transfer: Path,
) -> None:
    """Test failure of autosigning when there are no keys in the profile."""
    # ARRANGE
    for alias in cli_tester.world.profile.keys.get_all_aliases():
        cli_tester.configure_key_remove(alias=alias)

    # ACT $ ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLINoKeysAvailableError())):
        cli_tester.process_transaction(from_file=transaction_file_with_transfer)


async def test_negative_autosign_transaction_failure_due_to_multiple_keys_in_profile(
    cli_tester: CLITester,
    transaction_file_with_transfer: Path,
) -> None:
    """Test failure of autosigning when there are multiple keys in the profile."""
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT $ ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIMultipleKeysAutoSignError())):
        cli_tester.process_transaction(from_file=transaction_file_with_transfer)


async def test_default_autosign_with_force_unsign(
    cli_tester: CLITester, signed_transaction_file_with_transfer: Path
) -> None:
    """Test omitting autosign when 'force-unsign' flag is passed and 'autosign' flag is not explicit set."""
    # ACT
    result = cli_tester.process_transaction(
        from_file=signed_transaction_file_with_transfer,
        force_unsign=True,
        broadcast=False,
        save_file=signed_transaction_file_with_transfer,
    )

    # ASSERT
    assert_contains_transaction_loaded_message(result.stdout)
    assert_contains_transaction_saved_to_file_message(signed_transaction_file_with_transfer, result.stdout)
    assert_transaction_file_is_unsigned(signed_transaction_file_with_transfer)


async def test_negative_explicit_autosign_with_force_unsign(
    cli_tester: CLITester, signed_transaction_file_with_transfer: Path
) -> None:
    """Test error when passing 'autosign' with 'force-unsign' flags."""
    # ACT & ASSERT

    with pytest.raises(
        CLITestCommandError,
        match=get_formatted_error_message(CLIMutuallyExclusiveOptionsError("autosign", "force-unsign")),
    ):
        cli_tester.process_transaction(
            from_file=signed_transaction_file_with_transfer,
            force_unsign=True,
            broadcast=False,
            save_file=signed_transaction_file_with_transfer,
            autosign=True,
        )


@pytest.mark.parametrize("already_signed_mode", ["override", "multisign"])
async def test_negative_autosign_with_not_allowed_autosigned_mode(
    cli_tester: CLITester, transaction_file_with_transfer: Path, already_signed_mode: AlreadySignedMode
) -> None:
    """Test autosigning failure when 'already-signed-mode' is not 'strict'."""
    # ACT & ASSERT
    with pytest.raises(
        CLITestCommandError, match=get_formatted_error_message(CLIWrongAlreadySignedModeAutoSignError())
    ):
        cli_tester.process_transaction(
            from_file=transaction_file_with_transfer, already_signed_mode=already_signed_mode
        )
