from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import test_tools as tt
    from textual.screen import Screen
    from textual.widget import Widget

    from clive_local_tools.tui.types import CliveApp, ClivePilot
    from schemas.operations import AnyOperation
    from schemas.operations.representations import HF26Representation


def assert_is_screen_active(pilot: ClivePilot, expected_screen: type[Screen[Any]]) -> None:
    """Assert that the expected screen is active."""
    assert isinstance(
        pilot.app.screen, expected_screen
    ), f"Expected screen '{expected_screen}' is not active. Current screen is '{pilot.app.screen}'."


def assert_is_focused(pilot: ClivePilot, widget: type[Widget]) -> None:
    """Assert that the expected widget is focused."""
    assert isinstance(
        pilot.app.focused, widget
    ), f"Required the focus to be on `{widget}`, but is on `{pilot.app.focused}`."


def assert_is_key_binding_active(app: CliveApp, key: str, description: str | None = None) -> None:
    """Assert if key binding is active."""
    binding_description_map = {k: v[1].description for k, v in app.namespace_bindings.items()}

    message = f"Key binding for `{key}` is not available, Cannot proceed!\nCurrent ones are: {binding_description_map}"
    assert key in binding_description_map, message

    if description:
        stored_description = binding_description_map.get(key)

        message = (
            f"Key binding for `{key}` with description of `{description}` is not available, Cannot proceed!\n"
            f"Current ones are: {binding_description_map}"
        )
        assert stored_description == description, message


def assert_operations_placed_in_blockchain(
    node: tt.RawNode, transaction_id: str, *expected_operations: AnyOperation
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
