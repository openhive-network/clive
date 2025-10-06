from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.keys.keys import PrivateKey
from clive.__private.models.schemas import CustomJsonOperation, JsonString
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
    assert_transaction_in_blockchain,
)
from clive_local_tools.cli.checkers import assert_transaction_file_is_signed
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.types import AlreadySignedMode
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_TO_POWER_UP: Final[tt.Asset.HiveT] = tt.Asset.Hive(765.432)
AMOUNT_TO_TRANSFER: Final[tt.Asset.HiveT] = tt.Asset.Hive(345.456)
EXAMPLE_OBJECT: Final[str] = '{"foo": "bar"}'
EXAMPLE_STRING: Final[str] = '"somestring"'
EXAMPLE_NUMBER: Final[str] = "123456.789"
ID: Final[str] = "test-custom-json-some-id"
RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
ADDITIONAL_KEY_VALUE: str = PrivateKey.create().value
ADDITIONAL_KEY_ALIAS_NAME: Final[str] = f"{WORKING_ACCOUNT_KEY_ALIAS}_2"


def trx_file(temporary_path_per_test: Path) -> Path:
    return temporary_path_per_test / "trx.json"


def create_signed_transaction_file(cli_tester: CLITester, tmp_path: Path) -> Path:
    """Create a signed transaction file for multisig testing."""
    signed_transaction = tmp_path / "signed_trx.json"
    cli_tester.process_transfer(
        amount=AMOUNT_TO_TRANSFER,
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        broadcast=False,
        save_file=signed_transaction,
    )
    return signed_transaction


@pytest.mark.parametrize("json_", [EXAMPLE_OBJECT, EXAMPLE_STRING, EXAMPLE_NUMBER])
async def test_load_custom_json_from_file(node: tt.RawNode, cli_tester: CLITester, tmp_path: Path, json_: str) -> None:
    """Regression test for problem with parsing json field in CustomJsonOpetation saved in file."""
    # ARRANGE
    operation = CustomJsonOperation(
        required_auths=[],
        required_posting_auths=[WORKING_ACCOUNT_DATA.account.name],
        id_=ID,
        json_=JsonString(json_),
    )

    # ACT
    cli_tester.process_custom_json(
        authorize=WORKING_ACCOUNT_DATA.account.name,
        id_=ID,
        json_=json_,
        broadcast=False,
        save_file=trx_file(tmp_path),
        autosign=False,
    )

    result = cli_tester.process_transaction(
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        already_signed_mode="multisign",
        from_file=trx_file(tmp_path),
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_signed_transaction(
    node: tt.RawNode,
    cli_tester: CLITester,
    tmp_path: Path,
) -> None:
    """Check if clive process transaction loads signed transaction and broadcasts it."""
    # ARRANGE
    cli_tester.process_power_up(
        amount=AMOUNT_TO_POWER_UP,
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        broadcast=False,
        save_file=trx_file(tmp_path),
    )

    # ACT
    result = cli_tester.process_transaction(
        already_signed_mode="multisign",
        from_file=trx_file(tmp_path),
        autosign=False,
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_process_unsigned_transaction(
    node: tt.RawNode,
    cli_tester: CLITester,
    tmp_path: Path,
) -> None:
    """Check if clive process transactions loads unsigned transaction, signs and broadcasts it."""
    # ARRANGE
    cli_tester.process_power_up(
        amount=AMOUNT_TO_POWER_UP,
        to=RECEIVER,
        broadcast=False,
        save_file=trx_file(tmp_path),
        autosign=False,
    )

    # ACT
    result = cli_tester.process_transaction(
        already_signed_mode="multisign",
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        from_file=trx_file(tmp_path),
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_negative_process_transaction_in_locked(
    cli_tester: CLITester,
    tmp_path: Path,
) -> None:
    """Check if clive process transaction throws exception when wallet is not unlocked."""
    # ARRANGE
    message = CLINoProfileUnlockedError.MESSAGE
    cli_tester.process_power_up(
        amount=AMOUNT_TO_POWER_UP,
        to=RECEIVER,
        broadcast=False,
        save_file=trx_file(tmp_path),
    )
    beekeeper = cli_tester.world.beekeeper_manager.beekeeper
    await (await beekeeper.session).lock_all()
    cli_tester.world.profile.skip_saving()  # cannot save profile when it is locked because encryption is not possible

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=message):
        cli_tester.process_transaction(
            already_signed_mode="multisign",
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            from_file=trx_file(tmp_path),
        )


async def test_multisign_transaction(cli_tester: CLITester, tmp_path: Path) -> None:
    """Check if clive process transaction will place second signature with `already-signed-mode` set to `multisig`."""
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)
    signed_transaction = create_signed_transaction_file(cli_tester, tmp_path)
    multisigned_transaction = tmp_path / "multisig_trx.json"

    # ACT
    cli_tester.process_transaction(
        already_signed_mode="multisign",
        sign_with=ADDITIONAL_KEY_ALIAS_NAME,
        broadcast=False,
        from_file=signed_transaction,
        save_file=multisigned_transaction,
    )

    # ASSERT
    assert_transaction_file_is_signed(multisigned_transaction, signatures_count=2)


async def test_override_signature_in_transaction(cli_tester: CLITester, tmp_path: Path) -> None:
    """Check if clive process transaction will override signature with `already-signed-mode` set to `override`."""
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)
    signed_transaction = create_signed_transaction_file(cli_tester, tmp_path)
    override_transaction = tmp_path / "override_trx.json"

    # ACT
    cli_tester.process_transaction(
        already_signed_mode="override",
        broadcast=False,
        sign_with=ADDITIONAL_KEY_ALIAS_NAME,
        from_file=signed_transaction,
        save_file=override_transaction,
    )

    # ASSERT
    assert_transaction_file_is_signed(override_transaction, signatures_count=1)


@pytest.mark.parametrize("already_signed_mode", ["strict", None])
async def test_negative_error_placing_multisign(
    cli_tester: CLITester, tmp_path: Path, already_signed_mode: AlreadySignedMode | None
) -> None:
    """Check if clive process transaction will raise error with `already-signed-mode` set to `strict` or default."""
    # ARRANGE
    cli_tester.configure_key_add(key=ADDITIONAL_KEY_VALUE, alias=ADDITIONAL_KEY_ALIAS_NAME)
    signed_transaction = create_signed_transaction_file(cli_tester, tmp_path)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match="You cannot sign a transaction that is already signed."):
        cli_tester.process_transaction(
            already_signed_mode=already_signed_mode,
            sign_with=ADDITIONAL_KEY_ALIAS_NAME,
            broadcast=False,
            from_file=signed_transaction,
        )
