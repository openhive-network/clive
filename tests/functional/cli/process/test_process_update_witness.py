from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.models.schemas import TransferOperation
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-memo"


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_account_creation_fee(cli_tester_unlocked_with_witness_profile: CLITester, use_active_authority: bool) -> None:  # noqa: FBT001
    """Check clive process transfer command."""
    # ARRANGE
    breakpoint()
    amount = tt.Asset.Hive(3.456)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)).result_or_raise

    # ACT
    cli_tester_unlocked_with_witness_profile.process_update_witness(account_creation_fee=amount)

    # ASSERT
    breakpoint()
    assert witness.props.account_creation_fee is amount, f"Witness '{owner}' account creation fee should change after command witness-update"


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_maximum_block_size(node: tt.RawNode, cli_tester: CLITester, use_active_authority: bool) -> None:  # noqa: FBT001
    """Check clive process transfer command."""
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_hbd_interest_rate(node: tt.RawNode, cli_tester: CLITester, use_active_authority: bool) -> None:  # noqa: FBT001
    """Check clive process transfer command."""
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_new_signing_key(node: tt.RawNode, cli_tester: CLITester, use_active_authority: bool) -> None:  # noqa: FBT001
    """Check clive process transfer command."""
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_hbd_exchange_rate(node: tt.RawNode, cli_tester: CLITester, use_active_authority: bool) -> None:  # noqa: FBT001
    """Check clive process transfer command."""
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_url(node: tt.RawNode, cli_tester: CLITester, use_active_authority: bool) -> None:  # noqa: FBT001
    """Check clive process transfer command."""
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_account_subsidy_budget(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check clive process transfer command."""
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_account_subsidy_decay(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check clive process transfer command."""
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_two_operations_in_transaction(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check clive process transfer command."""
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_using_updated_witness_key(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Check clive process transfer command."""
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
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=MEMO,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
