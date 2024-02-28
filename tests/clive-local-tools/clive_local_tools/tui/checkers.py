from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from textual.screen import Screen
    from textual.widget import Widget

    from clive_local_tools.tui.types import CliveApp, ClivePilot


def assert_is_screen_active(pilot: ClivePilot, expected_screen: type[Screen[Any]]) -> None:
    """Assert that the expected screen is active."""
    assert isinstance(
        pilot.app.screen, expected_screen
    ), f"Expected screen '{expected_screen}' is not active. Current screen is '{pilot.app.screen}'."


def assert_is_focused(app: CliveApp, widget: type[Widget]) -> None:
    """Assert that the expected widget is focused."""
    message = f"Required the focus to be on `{widget}`, but is on `{app.focused}`."
    assert isinstance(app.focused, widget), message


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
