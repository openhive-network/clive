from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import EscrowInvalidDeadlineError, EscrowZeroAmountError
from clive.__private.models.schemas import EscrowTransferOperation, HiveDateTime
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

from .conftest import AGENT, FEE, HBD_AMOUNT, HIVE_AMOUNT, RECEIVER, get_future_datetime, get_past_datetime

ESCROW_ID_PAST_EXPIRATION = 701
ESCROW_ID_RELATIVE_DEADLINE = 800
ESCROW_ID_BOTH_ASSETS = 801

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_process_escrow_transfer(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow transfer command."""
    # ARRANGE
    ratification_deadline = get_future_datetime(1)
    escrow_expiration = get_future_datetime(7)
    escrow_id = 0

    operation = EscrowTransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=HiveDateTime(ratification_deadline),
        escrow_expiration=HiveDateTime(escrow_expiration),
        json_meta="",
    )

    # ACT
    result = cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_transfer_auto_id(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow transfer with auto-calculated escrow_id."""
    # ARRANGE
    ratification_deadline = get_future_datetime(1)
    escrow_expiration = get_future_datetime(7)

    # ACT - don't specify escrow_id, it should be auto-calculated
    result = cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT - the command should succeed
    assert result.exit_code == 0


async def test_process_escrow_transfer_with_hive(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow transfer with HIVE amount."""
    # ARRANGE
    ratification_deadline = get_future_datetime(1)
    escrow_expiration = get_future_datetime(7)
    escrow_id = 10
    hive_amount = tt.Asset.Test(50)
    hbd_amount = tt.Asset.Tbd(0)
    fee = tt.Asset.Test(1)

    operation = EscrowTransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=hbd_amount,
        hive_amount=hive_amount,
        fee=fee,
        ratification_deadline=HiveDateTime(ratification_deadline),
        escrow_expiration=HiveDateTime(escrow_expiration),
        json_meta="",
    )

    # ACT
    result = cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=hbd_amount,
        hive_amount=hive_amount,
        fee=fee,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_process_escrow_transfer_zero_amount_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that escrow transfer fails when both HBD and HIVE amounts are zero."""
    # ARRANGE
    ratification_deadline = get_future_datetime(1)
    escrow_expiration = get_future_datetime(7)
    escrow_id = 400
    zero_hbd = tt.Asset.Tbd(0)
    zero_hive = tt.Asset.Test(0)

    expected_error = get_formatted_error_message(EscrowZeroAmountError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_transfer(
            from_=WORKING_ACCOUNT_NAME,
            to=RECEIVER,
            agent=AGENT,
            escrow_id=escrow_id,
            hbd_amount=zero_hbd,
            hive_amount=zero_hive,
            fee=FEE,
            ratification_deadline=ratification_deadline,
            escrow_expiration=escrow_expiration,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_transfer_past_ratification_deadline_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that escrow transfer fails when ratification deadline is in the past."""
    # ARRANGE - get a past datetime (relative to node time, as CLI validates against head block time)
    past_ratification_deadline = get_past_datetime(1, node)
    escrow_expiration = get_future_datetime(7, node)
    escrow_id = 500

    expected_error = get_formatted_error_message(
        EscrowInvalidDeadlineError("Ratification deadline must be in the future.")
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_transfer(
            from_=WORKING_ACCOUNT_NAME,
            to=RECEIVER,
            agent=AGENT,
            escrow_id=escrow_id,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            fee=FEE,
            ratification_deadline=past_ratification_deadline,
            escrow_expiration=escrow_expiration,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_transfer_expiration_before_ratification_error(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test that escrow transfer fails when escrow expiration is before ratification deadline."""
    # ARRANGE - escrow_expiration equals ratification_deadline (should fail)
    ratification_deadline = get_future_datetime(7)
    escrow_expiration = get_future_datetime(1)  # Earlier than ratification
    escrow_id = 600

    expected_error = get_formatted_error_message(
        EscrowInvalidDeadlineError("Escrow expiration must be after ratification deadline.")
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_transfer(
            from_=WORKING_ACCOUNT_NAME,
            to=RECEIVER,
            agent=AGENT,
            escrow_id=escrow_id,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            fee=FEE,
            ratification_deadline=ratification_deadline,
            escrow_expiration=escrow_expiration,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_transfer_past_expiration_error(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test that escrow transfer fails when escrow expiration is in the past."""
    # ARRANGE - past expiration but future ratification
    ratification_deadline = get_future_datetime(1, node)
    escrow_expiration = get_past_datetime(1, node)

    expected_error = get_formatted_error_message(EscrowInvalidDeadlineError("Escrow expiration must be in the future."))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.process_escrow_transfer(
            from_=WORKING_ACCOUNT_NAME,
            to=RECEIVER,
            agent=AGENT,
            escrow_id=ESCROW_ID_PAST_EXPIRATION,
            hbd_amount=HBD_AMOUNT,
            hive_amount=HIVE_AMOUNT,
            fee=FEE,
            ratification_deadline=ratification_deadline,
            escrow_expiration=escrow_expiration,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        )


async def test_process_escrow_transfer_with_relative_deadline(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow transfer with relative deadline format (+1d, +7d)."""
    # ACT
    result = cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=ESCROW_ID_RELATIVE_DEADLINE,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline="+1d",
        escrow_expiration="+7d",
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert result.exit_code == 0


async def test_process_escrow_transfer_with_both_assets(
    node: tt.RawNode,
    cli_tester: CLITester,
) -> None:
    """Test clive process escrow transfer with both HBD and HIVE amounts non-zero."""
    # ARRANGE
    ratification_deadline = get_future_datetime(1)
    escrow_expiration = get_future_datetime(7)
    hbd_amount = tt.Asset.Tbd(10)
    hive_amount = tt.Asset.Test(50)

    operation = EscrowTransferOperation(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=ESCROW_ID_BOTH_ASSETS,
        hbd_amount=hbd_amount,
        hive_amount=hive_amount,
        fee=FEE,
        ratification_deadline=HiveDateTime(ratification_deadline),
        escrow_expiration=HiveDateTime(escrow_expiration),
        json_meta="",
    )

    # ACT
    result = cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=ESCROW_ID_BOTH_ASSETS,
        hbd_amount=hbd_amount,
        hive_amount=hive_amount,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
