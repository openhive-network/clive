from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from clive_local_tools.tui.checkers import assert_is_key_binding_active
from clive_local_tools.tui.constants import TUI_TESTS_GENERAL_TIMEOUT

if TYPE_CHECKING:
    from textual.screen import Screen

    from clive_local_tools.tui.types import ClivePilot


async def write_text(pilot: ClivePilot, text: str) -> None:
    """Useful for place text in any Input widget."""
    await pilot.press(*list(text))


async def press_binding(pilot: ClivePilot, key: str, key_description: str | None = None) -> None:
    """Safer version of pilot.press which ensures that the key binding is active and optionally asserts binding desc."""
    assert_is_key_binding_active(pilot.app, key, key_description)
    await pilot.press(key)


async def press_and_wait_for_screen(  # noqa: PLR0913
    pilot: ClivePilot,
    key: str,
    expected_screen: type[Screen[Any]],
    *,
    key_description: str | None = None,
    wait_for_focused: bool = True,
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,
) -> None:
    """Press some binding and ensure screen changed after some action."""
    await press_binding(pilot, key, key_description)
    await wait_for_screen(pilot, expected_screen, wait_for_focused=wait_for_focused, timeout=timeout)


async def wait_for_screen(
    pilot: ClivePilot,
    expected_screen: type[Screen[Any]],
    *,
    wait_for_focused: bool = True,
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,
) -> None:
    """Wait for the expected screen to be active."""

    async def wait_for_screen_change() -> None:
        while not isinstance(app.screen, expected_screen):
            await pilot.pause(poll_time_secs)

    async def wait_for_something_to_be_focused() -> None:
        while not app.focused:
            await pilot.pause(poll_time_secs)

    async def wait_for_everything() -> None:
        await wait_for_screen_change()
        if wait_for_focused:
            await wait_for_something_to_be_focused()

    poll_time_secs = 0.1
    app = pilot.app

    try:
        await asyncio.wait_for(wait_for_everything(), timeout=timeout)
    except asyncio.TimeoutError:
        wait_for_focused_info = " or nothing was focused " if wait_for_focused else " "
        raise AssertionError(
            f"Screen didn't changed to '{expected_screen}'{wait_for_focused_info}in {timeout=}s.\n"
            f"Current screen is: {app.screen}\n"
            f"Currently focused: {app.focused}"
        ) from None


async def focus_next(pilot: ClivePilot, timeout: float = TUI_TESTS_GENERAL_TIMEOUT) -> None:
    """Change focus to next Widget and wait for something is focused."""
    await pilot.press("tab")
    try:
        task = _wait_for_something_to_be_focused(pilot)
        await asyncio.wait_for(task, timeout=timeout)
    except asyncio.TimeoutError:
        app = pilot.app
        raise AssertionError(
            f"Nothing was focused in {timeout=}s.\n"
            f"Current screen is: {app.screen}\n"
            f"Currently focused: {app.focused}"
        ) from None
