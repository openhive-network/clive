from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.governance_operations.governance_operations import Governance
from clive.__private.ui.operations.governance_operations.witness.witness import (
    Witness,
    WitnessActionRow,
    WitnessNameLabel,
)
from clive.__private.ui.operations.operations import OperationButton, Operations
from clive_local_tools.tui.checkers import (
    assert_active_tab,
    assert_is_focused,
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.tui.finalize_transaction import finalize_transaction
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
    write_text,
)
from clive_local_tools.tui.utils import get_profile_name
from clive_local_tools.tui.witness_votes_utils import (
    USER2,
    WITNESSES_PER_PAGE,
    goto_first_witness,
    unvote_witness,
    vote_witness,
)

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot, OperationProcessing
    from schemas.operations import AccountWitnessVoteOperation


TESTDATA: Final[list[OperationProcessing]] = [
    "FAST_BROADCAST",
    "FINALIZE_TRANSACTION",
    "ADD_TO_CART",
]


@pytest.mark.parametrize("account", [USER2])
@pytest.mark.parametrize("operation_processing", TESTDATA)
async def test_witness_votes_user2_1(
    working_account: tt.Account,
    account: tt.Account,  # noqa: ARG001
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_processing: OperationProcessing,
) -> None:
    """
    1. Test cases: Vote for one witness.

        1.2. User 2 votes for one witness and then broadcast it (a/b/c).
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen
    tt.logger.debug(f"user profile: {get_profile_name(pilot.app)}")
    tt.logger.debug(f"working_account: {working_account}")

    # ACT
    await focus_next(pilot)  # go to first witness on list
    await goto_first_witness(pilot, "Vote")
    expected_operation = await vote_witness(pilot, USER2.name)
    await process_operation(pilot, operation_processing)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


@pytest.mark.parametrize("account", [USER2])
@pytest.mark.parametrize("operation_processing", TESTDATA)
async def test_witness_votes_user2_2(
    working_account: tt.Account,  # noqa: ARG001
    account: tt.Account,  # noqa: ARG001
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_processing: OperationProcessing,
) -> None:
    """
    2. Test cases: Remove a vote for one witness.

        2.1. User 2 removes a vote for one witness and then broadcast it (a/b/c).
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen
    tt.logger.debug(f"user profile: {get_profile_name(pilot.app)}")

    # ACT
    await focus_next(pilot)  # go to first witness on list
    expected_operation = await unvote_witness(pilot, USER2.name)
    await process_operation(pilot, operation_processing)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


@pytest.mark.parametrize("account", [USER2])
@pytest.mark.parametrize("operation_processing", TESTDATA)
async def test_witness_votes_user2_3(
    working_account: tt.Account,  # noqa: ARG001
    account: tt.Account,  # noqa: ARG001
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_processing: OperationProcessing,
) -> None:
    """
    3. Test cases: Add and remove votes for witnesses.

        3.2. User 2 votes for two witnesses (witness_04 and witness_05) and removes vote for witness_02 and then
             broadcast the transaction (a/b/c).
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen
    expected_operations: list[AccountWitnessVoteOperation] = []

    # ACT
    # Assumes order of witnesses: 02 03 01 04 05
    await focus_next(pilot)  # go to first witness on list
    expected_operations.append(await unvote_witness(pilot, USER2.name, "witness-02"))
    for _ in range(3):
        await focus_next(pilot)  # go to the next witness on list
    expected_operations.append(await vote_witness(pilot, USER2.name, "witness-04"))
    await focus_next(pilot)  # go to the next witness on list
    expected_operations.append(await vote_witness(pilot, USER2.name, "witness-05"))

    await process_operation(pilot, operation_processing)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)


@pytest.mark.parametrize("account", [USER2])
async def test_witness_votes_user2_4(
    working_account: tt.Account,  # noqa: ARG001
    account: tt.Account,  # noqa: ARG001
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """
    4. Test cases: Pending operations (cart).

        4.2. User removes an operation from cart.
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen

    # ACT
    await focus_next(pilot)  # go to first witness on list
    await goto_first_witness(pilot, "Vote")
    await vote_witness(pilot, USER2.name)  # this operation will be removed
    await focus_next(pilot)  # go to the next witness on list
    expected_operation = await vote_witness(pilot, USER2.name)

    await press_and_wait_for_screen(pilot, "f2", Operations)  # add 2 operations to cart
    await press_and_wait_for_screen(pilot, "f2", Cart)
    await focus_next(pilot)  # go to first operation on list
    await pilot.press("enter")  # remove operation from cart

    await press_and_wait_for_screen(pilot, "escape", Operations)  # back to Operations
    assert_is_focused(pilot, OperationButton)
    await press_and_wait_for_screen(pilot, "enter", Governance)
    assert_active_tab(pilot, "Proxy")
    await pilot.press("right")
    assert_active_tab(pilot, "Witnesses")

    # ASSERT
    actions = pilot.app.screen.query(WitnessActionRow)
    assert len(actions) == 1, f"Expected single pending action! Current number is: {len(actions)} action(s)."

    # ACT
    await press_and_wait_for_screen(pilot, "escape", Operations)
    await press_and_wait_for_screen(pilot, "f2", Cart)
    await finalize_transaction(pilot)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


@pytest.mark.parametrize("account", [USER2])
async def test_witness_votes_user2_5(
    working_account: tt.Account,  # noqa: ARG001
    account: tt.Account,  # noqa: ARG001
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """
    5. Test cases: Cart and other way of broadcast.

        5.1. Cart and fast broadcast - User 2 has operations in the cart and fast broadcast another operations.
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen

    # ACT
    # Assumes order of witnesses: 02 03 01 04 05, so skip some witnesses
    for _ in range(3):
        await focus_next(pilot)  # go to next witness on list
        assert_is_focused(pilot, Witness)

    VOTES: Final[int] = 2  # noqa: N806

    for i in range(VOTES):
        await focus_next(pilot)  # go to next witness on list
        await vote_witness(pilot, USER2.name, f"witness-0{4+i}")

    await press_and_wait_for_screen(pilot, "f2", Operations)  # add 2 operations to cart
    # Back to Witnesses view
    assert_is_focused(pilot, OperationButton)
    await press_and_wait_for_screen(pilot, "enter", Governance)
    assert_active_tab(pilot, "Proxy")
    await pilot.press("right")
    assert_active_tab(pilot, "Witnesses")

    await focus_next(pilot)  # go to first witness on list
    expected_operation = await unvote_witness(pilot, USER2.name, "witness-02")

    await process_operation(pilot, "FAST_BROADCAST")

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # Back to Witnesses page
    await press_and_wait_for_screen(pilot, "enter", Governance)
    assert_active_tab(pilot, "Proxy")
    await pilot.press("right")
    assert_active_tab(pilot, "Witnesses")

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)
    actions = pilot.app.screen.query(WitnessActionRow)
    assert len(actions) == VOTES, f"Expected {VOTES}pending actions! Current number is: {len(actions)} action(s)."


@pytest.mark.parametrize("account", [USER2])
async def test_witness_votes_user2_6(
    working_account: tt.Account,  # noqa: ARG001
    account: tt.Account,  # noqa: ARG001
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """
    6. Test cases: Check if the sorting is correct.

        6.1. For user 2. The order should be: witness_02, witness_03 and then witness_01 and witness_04 etc.
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen
    WITNESSES: Final[tuple[str, str, str, str, str]] = (  # noqa: N806
        "witness-02",
        "witness-03",
        "witness-01",
        "witness-04",
        "witness-05",
    )

    # ACT
    # Assumes order of witnesses: 02 03 01 04 05
    # ACT & ASSERT
    await focus_next(pilot)  # go to first witness on list
    for witness in WITNESSES:
        if witness in ("witness-02", "witness-03"):
            await unvote_witness(pilot, USER2.name, witness)
        else:
            await vote_witness(pilot, USER2.name, witness)
        await focus_next(pilot)  # go to next witness on list


@pytest.mark.parametrize("account", [USER2])
async def test_witness_votes_user2_7(
    working_account: tt.Account,  # noqa: ARG001
    account: tt.Account,  # noqa: ARG001
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """
    8. Test cases: Searching the witnesses.

        8.1. User 2: Search 'witness_01', limit = 1 - Should be one result 'witness_01'.
            Check that 'Clear' removes the results.
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen
    WITNESS_NAME: Final[str] = "witness-01"  # noqa: N806

    # ACT
    for _ in range(WITNESSES_PER_PAGE + 1):
        await focus_next(pilot)  # go to next witness on list

    await write_text(pilot, WITNESS_NAME)
    await focus_next(pilot)
    await pilot.press("ctrl+w")
    await write_text(pilot, "1")
    await focus_next(pilot)
    await pilot.press("enter")

    # ASSERT
    witness: Witness = pilot.app.screen.query_one(Witness)
    label = witness.query_one(WitnessNameLabel)
    text = str(label.renderable)
    assert text == WITNESS_NAME, f"Expected '{WITNESS_NAME}' witness name, current is '{text}'"

    # ACT
    await focus_next(pilot)
    await pilot.press("enter")

    # ASSERT
    witnesses = pilot.app.screen.query(Witness)
    assert (
        len(witnesses) == WITNESSES_PER_PAGE
    ), f"Expected {WITNESSES_PER_PAGE} witnesses in view! Current number is: {len(witnesses)} witness(es)."


@pytest.mark.parametrize("account", [USER2])
async def test_witness_votes_user2_8(
    working_account: tt.Account,  # noqa: ARG001
    account: tt.Account,  # noqa: ARG001
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """
    8. Test cases: Searching the witnesses.

        8.2. User 2: Search 'witness_1', limit = 10 - should be 10 results.
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen
    WITNESS_NAME: Final[str] = "witness-1"  # noqa: N806
    WITNESSES_COUNT: Final[int] = 10  # noqa: N806

    # ACT
    for _ in range(WITNESSES_PER_PAGE + 1):
        await focus_next(pilot)  # go to next witness on list

    # check if 'Witness name' input focused
    await write_text(pilot, WITNESS_NAME)
    await focus_next(pilot)
    # check if 'Limit' input focused
    await pilot.press("ctrl+w")
    await write_text(pilot, str(WITNESSES_COUNT))
    await focus_next(pilot)
    # check if 'Search' button focused
    await pilot.press("enter")

    # ASSERT
    witnesses = pilot.app.screen.query(Witness)
    assert (
        len(witnesses) == WITNESSES_COUNT
    ), f"Expected {WITNESSES_COUNT} witnesses in view! Current number is: {len(witnesses)} witness(es)."
