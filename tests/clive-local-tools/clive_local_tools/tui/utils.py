from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt
from textual.css.query import NoMatches

from clive.__private.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from textual.app import App

    from schemas.operations import AnyOperation
    from schemas.operations.representations import HF26Representation


def get_mode(app: App[int]) -> str:
    """Do not call while onboarding process."""
    try:
        widget = app.query_one("#mode-label", TitledLabel)
    except NoMatches as error:
        raise AssertionError("Mode couldn't be found. It is not available in the onboarding process.") from error
    return str(widget.value).strip()


def log_current_view(app: App[int], *, nodes: bool = False) -> None:
    """For debug purposes."""
    tt.logger.debug(f"screen: {app.screen}, focused: {app.focused}")
    if nodes:
        tt.logger.debug(f'nodes: {app.query("*").nodes}')


def assert_operations_placed_in_blockchain(
    node: tt.InitNode, transaction_id: str, *expected_operations: AnyOperation
) -> None:
    transaction = node.api.account_history.get_transaction(
        id=transaction_id, include_reversible=True  # type: ignore[call-arg] # TODO: id -> id_ after helpy bug fixed
    )
    operations_to_check = list(expected_operations)
    for operation_representation in transaction.operations:
        _operation_representation: HF26Representation[AnyOperation] = operation_representation
        operation = _operation_representation.value
        if operation in operations_to_check:
            operations_to_check.remove(operation)

    message = (
        "Operations missing in blockchain.\n"
        f"Operations: {operations_to_check}\n"
        "were not found in the transaction:\n"
        f"{transaction}."
    )
    assert not operations_to_check, message
