from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from clive_local_tools.tui.checkers import assert_is_key_binding_active

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


async def press_and_wait_for_screen(
    pilot: ClivePilot,
    key: str,
    expected_screen: type[Screen[Any]],
    *,
    key_description: str | None = None,
    timeout: float = 3.0,
) -> None:
    """Press some binding and ensure screen changed after some action."""
    await press_binding(pilot, key, key_description)
    await wait_for_screen(pilot, expected_screen, timeout=timeout)


async def press_and_wait_for_screen_focused(
    pilot: ClivePilot,
    key: str,
    expected_screen: type[Screen[Any]],
    *,
    key_description: str | None = None,
    timeout: float = 3.0,
) -> None:
    """Press some binding and ensure screen changed after some action."""
    await press_binding(pilot, key, key_description)
    await wait_for_screen(pilot, expected_screen, focused=True, timeout=timeout)


async def wait_for_screen(
    pilot: ClivePilot, expected_screen: type[Screen[Any]], *, focused: bool = False, timeout: float = 3.0
) -> None:
    """Wait for the expected screen to be active."""

    async def wait_for_screen_change() -> None:
        while not isinstance(app.focused if focused is True else app.screen, expected_screen):
            await pilot.pause(0.1)

    app = pilot.app

    try:
        await asyncio.wait_for(wait_for_screen_change(), timeout=timeout)
    except asyncio.TimeoutError:
        actual_screen = "Focused" if focused is True else "Current"
        actual_screen += f" one is: {app.focused if focused is True else app.screen}"
        raise AssertionError(f"Screen didn't changed to '{expected_screen}' in {timeout=}. " + actual_screen) from None
