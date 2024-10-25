from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from textual.css.query import NoMatches, TooManyMatches

from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.widgets.currency_selector.currency_selector_base import CurrencySelectorBase
from clive.__private.ui.widgets.inputs.clive_input import CliveInput

if TYPE_CHECKING:
    from textual.screen import Screen
    from textual.widget import Widget

    from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
    from clive_local_tools.tui.types import CliveApp, ClivePilot


def assert_is_screen_active(pilot: ClivePilot, expected_screen: type[Screen[Any]]) -> None:
    """Assert that the expected screen is active."""
    assert isinstance(
        pilot.app.screen, expected_screen
    ), f"Expected screen '{expected_screen}' is not active. Current screen is '{pilot.app.screen}'."


def assert_is_dashboard(pilot: ClivePilot) -> None:
    """
    Assert that the dashboard is the active screen.

    Args:
    ----
        pilot: ClivePilot instance.
    """
    assert_is_screen_active(pilot, Dashboard)


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
    target: Literal["input", "select"] = "input",
    context: str | None = None,
) -> None:
    composed_input_instance = (
        pilot.app.screen.query_exactly_one(composed_input) if isinstance(composed_input, type) else composed_input
    )

    context_details = f"Context: {context}" if context else ""

    def query_exactly_one_in_composed_input(query: str | type[Widget]) -> Widget:
        try:
            widget = composed_input_instance.query_exactly_one(query)
        except NoMatches as error:
            raise AssertionError(
                f"{composed_input_instance}.query_exactly_one('{query}') failed.\n"
                f"Expected {target=} couldn't be found in such a composed input. Are you sure it consists of it?\n"
                f"{context_details}"
            ) from error
        except TooManyMatches as error:
            raise AssertionError(
                f"{composed_input_instance}.query_exactly_one('{query}') with {target=} returns more than one widget.\n"
                f"Probably changed structure in such composed input.\n"
                f"{context_details}"
            ) from error
        return widget

    if target == "input":
        widget = query_exactly_one_in_composed_input(CliveInput)
    elif target == "select":
        widget = query_exactly_one_in_composed_input(CurrencySelectorBase)

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
