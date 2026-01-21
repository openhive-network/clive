from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive.__private.models.schemas import CollateralizedConvertOperation, ConvertOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


AMOUNT_HBD: Final[tt.Asset.HbdT] = tt.Asset.Hbd(10.000)
AMOUNT_HIVE: Final[tt.Asset.HiveT] = tt.Asset.Hive(10.000)


async def test_convert_hbd_to_hive(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test standard conversion from HBD to HIVE (3.5 days waiting period)."""
    # ARRANGE
    operation = ConvertOperation(
        owner=WORKING_ACCOUNT_DATA.account.name,
        requestid=0,
        amount=AMOUNT_HBD,
    )

    # ACT
    result = cli_tester.process_convert(
        amount=AMOUNT_HBD,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_convert_hive_to_hbd(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test collateralized conversion from HIVE to HBD."""
    # ARRANGE
    operation = CollateralizedConvertOperation(
        owner=WORKING_ACCOUNT_DATA.account.name,
        requestid=0,
        amount=AMOUNT_HIVE,
    )

    # ACT
    result = cli_tester.process_convert(
        amount=AMOUNT_HIVE,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_convert_with_custom_request_id(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test conversion with custom request_id."""
    # ARRANGE
    custom_request_id = 42
    operation = ConvertOperation(
        owner=WORKING_ACCOUNT_DATA.account.name,
        requestid=custom_request_id,
        amount=AMOUNT_HBD,
    )

    # ACT
    result = cli_tester.process_convert(
        amount=AMOUNT_HBD,
        request_id=custom_request_id,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_convert_request_id_counted_separately(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Test that request_id is counted separately for HBD and HIVE conversions."""
    # ARRANGE
    hbd_op1 = ConvertOperation(
        owner=WORKING_ACCOUNT_DATA.account.name,
        requestid=0,
        amount=AMOUNT_HBD,
    )
    hive_op1 = CollateralizedConvertOperation(
        owner=WORKING_ACCOUNT_DATA.account.name,
        requestid=0,
        amount=AMOUNT_HIVE,
    )
    hbd_op2 = ConvertOperation(
        owner=WORKING_ACCOUNT_DATA.account.name,
        requestid=1,
        amount=AMOUNT_HBD,
    )

    # ACT & ASSERT
    # First HBD conversion - should get request_id=0
    result1 = cli_tester.process_convert(amount=AMOUNT_HBD, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
    assert_operations_placed_in_blockchain(node, result1, hbd_op1)

    # First HIVE conversion - should also get request_id=0 (separate namespace)
    result2 = cli_tester.process_convert(amount=AMOUNT_HIVE, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
    assert_operations_placed_in_blockchain(node, result2, hive_op1)

    # Second HBD conversion - should get request_id=1
    result3 = cli_tester.process_convert(amount=AMOUNT_HBD, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
    assert_operations_placed_in_blockchain(node, result3, hbd_op2)
