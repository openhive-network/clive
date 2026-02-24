from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.wax_operation_wrapper import WaxRcDelegationWrapper
from clive.__private.models.schemas import CustomJsonOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.checkers import assert_contains_dry_run_message, assert_output_contains
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


RC_DELEGATION_AMOUNT: Final[tt.Asset.VestT] = tt.Asset.Vest(5_000)
DELEGATEE_ACCOUNT_NAME: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name


async def test_rc_delegations_set(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_rc_delegations_set(
        delegatee=DELEGATEE_ACCOUNT_NAME, amount=RC_DELEGATION_AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    expected_op = WaxRcDelegationWrapper.create_delegation(
        from_account=WORKING_ACCOUNT_NAME,
        delegatee=DELEGATEE_ACCOUNT_NAME,
        max_rc=int(RC_DELEGATION_AMOUNT.amount),
    ).to_schemas(cli_tester.world.wax_interface, CustomJsonOperation)
    assert_operations_placed_in_blockchain(node, result, expected_op)


async def test_rc_delegations_remove(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    cli_tester.process_rc_delegations_set(
        delegatee=DELEGATEE_ACCOUNT_NAME, amount=RC_DELEGATION_AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ACT
    result = cli_tester.process_rc_delegations_remove(
        delegatee=DELEGATEE_ACCOUNT_NAME, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    expected_op = WaxRcDelegationWrapper.create_removal(
        from_account=WORKING_ACCOUNT_NAME,
        delegatee=DELEGATEE_ACCOUNT_NAME,
    ).to_schemas(cli_tester.world.wax_interface, CustomJsonOperation)
    assert_operations_placed_in_blockchain(node, result, expected_op)
    show_result = cli_tester.show_rc()
    assert_output_contains("No outgoing RC delegations", show_result)


async def test_negative_rc_delegations_set_amount_below_minimum(cli_tester: CLITester) -> None:
    # ARRANGE
    too_small_amount = tt.Asset.Vest(1)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match="is below the minimum threshold"):
        cli_tester.process_rc_delegations_set(
            delegatee=DELEGATEE_ACCOUNT_NAME, amount=too_small_amount, sign_with=WORKING_ACCOUNT_KEY_ALIAS
        )


async def test_negative_rc_delegations_set_same_amount_as_existing(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    result = cli_tester.process_rc_delegations_set(
        delegatee=DELEGATEE_ACCOUNT_NAME, amount=RC_DELEGATION_AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )
    expected_op = WaxRcDelegationWrapper.create_delegation(
        from_account=WORKING_ACCOUNT_NAME,
        delegatee=DELEGATEE_ACCOUNT_NAME,
        max_rc=int(RC_DELEGATION_AMOUNT.amount),
    ).to_schemas(cli_tester.world.wax_interface, CustomJsonOperation)
    assert_operations_placed_in_blockchain(node, result, expected_op)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match="with the same amount"):
        cli_tester.process_rc_delegations_set(
            delegatee=DELEGATEE_ACCOUNT_NAME, amount=RC_DELEGATION_AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
        )


async def test_negative_rc_delegations_set_insufficient_rc(cli_tester: CLITester) -> None:
    # ARRANGE
    too_large_amount = tt.Asset.Vest(999_999_999)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match="Insufficient RC to delegate"):
        cli_tester.process_rc_delegations_set(
            delegatee=DELEGATEE_ACCOUNT_NAME, amount=too_large_amount, sign_with=WORKING_ACCOUNT_KEY_ALIAS
        )


async def test_rc_delegations_update(node: tt.RawNode, cli_tester: CLITester) -> None:
    """Update an existing delegation to a different amount — exercises the delta computation path."""
    # ARRANGE
    initial_result = cli_tester.process_rc_delegations_set(
        delegatee=DELEGATEE_ACCOUNT_NAME, amount=RC_DELEGATION_AMOUNT, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )
    assert_operations_placed_in_blockchain(
        node,
        initial_result,
        WaxRcDelegationWrapper.create_delegation(
            from_account=WORKING_ACCOUNT_NAME,
            delegatee=DELEGATEE_ACCOUNT_NAME,
            max_rc=int(RC_DELEGATION_AMOUNT.amount),
        ).to_schemas(cli_tester.world.wax_interface, CustomJsonOperation),
    )

    # ACT
    updated_amount = tt.Asset.Vest(10_000)
    result = cli_tester.process_rc_delegations_set(
        delegatee=DELEGATEE_ACCOUNT_NAME, amount=updated_amount, sign_with=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_operations_placed_in_blockchain(
        node,
        result,
        WaxRcDelegationWrapper.create_delegation(
            from_account=WORKING_ACCOUNT_NAME,
            delegatee=DELEGATEE_ACCOUNT_NAME,
            max_rc=int(updated_amount.amount),
        ).to_schemas(cli_tester.world.wax_interface, CustomJsonOperation),
    )


async def test_rc_delegations_set_dry_run(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_rc_delegations_set(
        delegatee=DELEGATEE_ACCOUNT_NAME, amount=RC_DELEGATION_AMOUNT, broadcast=False
    )

    # ASSERT
    assert result.exit_code == 0
    assert_contains_dry_run_message(result.output)


async def test_negative_rc_delegations_remove_non_existent(cli_tester: CLITester) -> None:
    # ACT & ASSERT — blockchain rejects removing a delegation that does not exist
    with pytest.raises(CLITestCommandError, match="Cannot delegate 0 if you are creating new rc delegation"):
        cli_tester.process_rc_delegations_remove(delegatee=DELEGATEE_ACCOUNT_NAME, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
