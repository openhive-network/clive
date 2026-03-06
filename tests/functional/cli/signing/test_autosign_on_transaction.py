from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import (
    CLIAuthorityPrefetchAutoSignError,
    CLIMutuallyExclusiveOptionsError,
    CLINoKeysAvailableError,
    CLITransactionNotSignedError,
)
from clive.__private.core.keys.keys import PrivateKey
from clive.__private.models.schemas import TransferOperation
from clive_local_tools.checkers.blockchain_checkers import assert_transaction_in_blockchain
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
from clive_local_tools.helpers import (
    create_transaction_file,
    create_transaction_filepath,
    get_formatted_error_message,
    get_signatures_count_from_output,
)
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.types import EnvContextFactory


AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(10)
TO_ACCOUNT: Final[str] = WATCHED_ACCOUNTS_NAMES[0]
AUTO_SIGN_SKIPPED_WARNING_MESSAGE: Final[str] = "Your transaction is already signed. Autosign will be skipped"
ADDITIONAL_KEY_VALUE: str = PrivateKey.generate().value
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
        already_signed_mode="strict",
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
    result = cli_tester.process_transaction(
        from_file=signed_transaction_file_with_transfer, broadcast=False, already_signed_mode="strict"
    )

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
    result = cli_tester.process_transaction(
        from_file=signed_transaction_file_with_transfer, broadcast=False, already_signed_mode="strict"
    )

    # ASSERT
    assert_auto_sign_skipped_warning_message_in_output(result.stdout)
    assert_contains_transaction_loaded_message(result.stdout)
    assert_contains_dry_run_message(result.stdout)


@pytest.mark.parametrize("broadcast", [None, True], ids=["default broadcast", "explicit broadcast"])
async def test_negative_autosign_transaction_failure_due_to_no_keys_in_profile(
    cli_tester: CLITester,
    transaction_file_with_transfer: Path,
    *,
    broadcast: bool | None,
) -> None:
    """Test failure of autosigning when there are no keys in the profile."""
    # ARRANGE
    for alias in cli_tester.world.profile.keys.get_all_aliases():
        cli_tester.configure_key_remove(alias=alias)

    # ACT $ ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLINoKeysAvailableError())):
        cli_tester.process_transaction(from_file=transaction_file_with_transfer, broadcast=broadcast)


async def test_autosign_transaction_with_multiple_keys_in_profile(
    cli_tester: CLITester,
    transaction_file_with_transfer: Path,
) -> None:
    """Test autosigning transaction when there are multiple different keys in the profile."""
    # ARRANGE
    signed_transaction_filepath = create_transaction_filepath("signed_multi_key")
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)

    # ACT
    result = cli_tester.process_transaction(
        from_file=transaction_file_with_transfer, save_file=signed_transaction_filepath
    )

    # ASSERT
    assert_contains_transaction_saved_to_file_message(signed_transaction_filepath, result.stdout)
    assert_transaction_file_is_signed(signed_transaction_filepath)


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


@pytest.mark.parametrize("extra_keys_count", [1, 2, 3])
async def test_autosign_transaction_with_matching_key_among_unrelated_keys(
    cli_tester: CLITester,
    transaction_file_with_transfer: Path,
    extra_keys_count: int,
) -> None:
    """Test autosigning succeeds when the matching key is present alongside unrelated keys."""
    # ARRANGE
    signed_transaction_filepath = create_transaction_filepath("signed_with_unrelated")
    for i in range(extra_keys_count):
        cli_tester.configure_key_add(key=PrivateKey.generate().value, alias=f"unrelated_key_{i}")
    await cli_tester.world.load_profile_based_on_beekepeer()
    assert len(cli_tester.world.profile.keys) == 1 + extra_keys_count

    # ACT
    result = cli_tester.process_transaction(
        from_file=transaction_file_with_transfer, save_file=signed_transaction_filepath
    )

    # ASSERT
    assert_contains_transaction_saved_to_file_message(signed_transaction_filepath, result.stdout)
    assert_transaction_file_is_signed(signed_transaction_filepath)


async def test_negative_autosign_transaction_with_no_matching_keys(
    cli_tester: CLITester,
    transaction_file_with_transfer: Path,
) -> None:
    """Test autosigning failure when wallet has keys but none match the transaction's required authorities."""
    # ARRANGE - remove the real key and add two unrelated generated keys
    for alias in cli_tester.world.profile.keys.get_all_aliases():
        cli_tester.configure_key_remove(alias=alias)
    cli_tester.configure_key_add(key=PrivateKey.generate().value, alias="unrelated_key_1")
    cli_tester.configure_key_add(key=PrivateKey.generate().value, alias="unrelated_key_2")

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLITransactionNotSignedError())):
        cli_tester.process_transaction(from_file=transaction_file_with_transfer)


async def test_negative_autosign_failure_due_to_unavailable_node(
    cli_tester: CLITester,
    node_address_env_context_factory: EnvContextFactory,
) -> None:
    """Test autosign failure when the node is unavailable during authority prefetching."""
    # ARRANGE - build an unsigned transaction with TAPOS while the node is still available
    unsigned_transaction_path = create_transaction_filepath("power_up_unsigned")
    cli_tester.process_power_up(
        from_=WORKING_ACCOUNT_NAME,
        amount=AMOUNT,
        save_file=unsigned_transaction_path,
        broadcast=False,
        autosign=False,
    )

    # ACT & ASSERT - with node unavailable, autosign fails fetching authorities
    with (
        node_address_env_context_factory("http://127.0.0.1:1"),
        pytest.raises(CLITestCommandError, match=get_formatted_error_message(CLIAuthorityPrefetchAutoSignError())),
    ):
        cli_tester.process_transaction(from_file=unsigned_transaction_path, broadcast=True)


SECOND_KEY_ALIAS: Final[str] = "second_active_key"


async def test_autosign_multisign_mode_accumulates_signatures(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test autosign in multisign mode: first sign explicitly with one key, then autosign adds the second key."""
    # ARRANGE - set up alice's active authority to require 2 signatures
    second_private_key = PrivateKey.generate()
    second_public_key = second_private_key.calculate_public_key()

    cli_tester.configure_key_add(key=second_private_key.value, alias=SECOND_KEY_ALIAS)

    cli_tester.process_update_authority(
        "active",
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        threshold=2,
    ).add_key(
        key=second_public_key.value,
        weight=1,
    ).fire()

    node.wait_number_of_blocks(1)

    # Sign the transfer with alice's key only and save to file (not broadcast)
    partial_signed_filepath = create_transaction_filepath("partial_signed_transfer")
    cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=AMOUNT,
        to=TO_ACCOUNT,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        broadcast=False,
        save_file=partial_signed_filepath,
        autosign=False,
    )
    assert_transaction_file_is_signed(partial_signed_filepath, signatures_count=1)

    # ACT - autosign adds second key's signature via multisign mode and broadcasts
    result = cli_tester.process_transaction(
        from_file=partial_signed_filepath,
        already_signed_mode="multisign",
        broadcast=True,
    )

    # ASSERT - transaction broadcasted with 2 signatures
    assert get_signatures_count_from_output(result.stdout) == 2  # noqa: PLR2004
    assert_transaction_in_blockchain(node, result)
