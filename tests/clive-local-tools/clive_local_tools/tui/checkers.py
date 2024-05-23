from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from textual.css.query import NoMatches, TooManyMatches

from clive.__private.ui.widgets.clive_tabbed_content import CliveTabs
from clive.__private.ui.widgets.currency_selector.currency_selector_base import CurrencySelectorBase
from clive.__private.ui.widgets.inputs.clive_input import CliveInput

if TYPE_CHECKING:
    import test_tools as tt
    from textual.screen import Screen
    from textual.widget import Widget
    from textual.widgets import Tab

    from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
    from clive_local_tools.tui.types import CliveApp, ClivePilot
    from schemas.operations import AnyOperation
    from schemas.operations.representations import HF26Representation


def assert_is_screen_active(pilot: ClivePilot, expected_screen: type[Screen[Any]]) -> None:
    """Assert that the expected screen is active."""
    assert isinstance(
        pilot.app.screen, expected_screen
    ), f"Expected screen '{expected_screen}' is not active. Current screen is '{pilot.app.screen}'."


def assert_is_focused(pilot: ClivePilot, widget: type[Widget] | Widget, context: str | None = None) -> None:
    """Assert that the expected widget is focused."""
    context_details = f"\nContext: {context}" if context else ""
    if isinstance(widget, type):
        assert isinstance(
            pilot.app.focused, widget
        ), f"Required the focus to be on `{widget}`, but is on `{pilot.app.focused}`.{context_details}"
    else:
        assert (
            widget.has_focus
        ), f"Required the focus to be on `{widget}`, but is on `{pilot.app.focused}`.{context_details}"


def assert_is_clive_composed_input_focused(
    pilot: ClivePilot,
    composed_input: type[CliveValidatedInput[Any]] | CliveValidatedInput[Any],
    *,
    target: Literal["input", "select", "known"] = "input",
    context: str | None = None,
) -> None:
    composed_input_instance = (
        pilot.app.screen.query_one(composed_input) if isinstance(composed_input, type) else composed_input
    )

    context_details = f"Context: {context}" if context else ""

    def query_one_in_composed_input(query: str | type[Widget]) -> Widget:
        try:
            widget = composed_input_instance.query_one(query)
        except NoMatches as error:
            raise AssertionError(
                f"{composed_input_instance}.query_one('{query}') failed.\n"
                f"Expected {target=} couldn't be found in such a composed input. Are you sure it consists of it?\n"
                f"{context_details}"
            ) from error
        except TooManyMatches as error:
            raise AssertionError(
                f"{composed_input_instance}.query_one('{query}') with {target=} returns more than one widget.\n"
                f"Probably changed structure in such composed input.\n"
                f"{context_details}"
            ) from error
        return widget

    if target == "input":
        widget = query_one_in_composed_input(CliveInput)
    elif target == "select":
        widget = query_one_in_composed_input(CurrencySelectorBase)
    elif target == "known":
        widget = query_one_in_composed_input("KnownAccount Checkbox")

    assert_is_focused(pilot, widget, context)


def assert_is_key_binding_active(app: CliveApp, key: str, description: str | None = None) -> None:
    """Assert if key binding is active."""
    binding_description_map = {k: v[1].description for k, v in app.active_bindings.items()}

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
        id=transaction_id,
        include_reversible=True,  # type: ignore[call-arg] # TODO: id -> id_ after helpy bug fixed
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


def assert_active_tab(pilot: ClivePilot, expected_label: str) -> None:
    assert_is_focused(pilot, CliveTabs)
    tabs: CliveTabs = pilot.app.focused  # type: ignore[assignment]
    tab: Tab = tabs.active_tab  # type: ignore[assignment]
    assert (
        tab.label_text == expected_label
    ), f"Expected '{expected_label}' tab to be active! Active tab is '{tab.label_text}'."
