from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import test_tools as tt

from clive.__private.ui.screens.dashboard import Dashboard
from clive_local_tools.tui.checkers import assert_is_key_binding_active
from clive_local_tools.tui.constants import TUI_TESTS_GENERAL_TIMEOUT

if TYPE_CHECKING:
    from typing import Final

    from textual.screen import Screen
    from textual.widget import Widget

    from clive_local_tools.tui.types import ClivePilot


POLL_TIME_SECS: Final[float] = 0.1


async def write_text(pilot: ClivePilot, text: str) -> None:
    """Place text in any Input widget."""
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
    if isinstance(pilot.app.screen, Dashboard):
        await wait_for_accounts_data(pilot)
    await press_binding(pilot, key, key_description)
    await wait_for_screen(pilot, expected_screen, wait_for_focused=wait_for_focused, timeout=timeout)


async def press_and_wait_for_focus(
    pilot: ClivePilot,
    key: str,
    *,
    key_description: str | None = None,
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,
) -> None:
    """Press some binding and ensure focus changed after some action."""
    current_focus = pilot.app.focused
    await press_binding(pilot, key, key_description)
    await wait_for_focus(pilot, different_than=current_focus, timeout=timeout)


async def _wait_for_screen_change(pilot: ClivePilot, expected_screen: type[Screen[Any]]) -> None:
    app = pilot.app
    while not isinstance(app.screen, expected_screen):
        await pilot.pause(POLL_TIME_SECS)


async def _wait_for_accounts_data(pilot: ClivePilot) -> None:
    while (
        not pilot.app.world.profile.accounts.is_tracked_accounts_node_data_available
        or not pilot.app.world.profile.accounts.is_tracked_accounts_alarms_data_available
    ):
        tt.logger.debug("Waiting for accounts node and alarms data...")
        await pilot.pause(POLL_TIME_SECS)


async def wait_for_accounts_data(pilot: ClivePilot, timeout: float = TUI_TESTS_GENERAL_TIMEOUT) -> None:
    try:
        await asyncio.wait_for(_wait_for_accounts_data(pilot), timeout=timeout)
    except TimeoutError:
        wait_for_node_data_info = (
            f"Waited too long for the accounts node or alarms data. Hasn't arrived in {timeout:.2f}s."
        )
        raise AssertionError(wait_for_node_data_info) from None


async def _wait_for_focus(pilot: ClivePilot, *, different_than: Widget | None = None) -> None:
    """Wait for focus set to anything if different_than is None or for change if not None."""
    app = pilot.app
    while not app.focused or app.focused is different_than:
        await pilot.pause(POLL_TIME_SECS)


async def wait_for_screen(
    pilot: ClivePilot,
    expected_screen: type[Screen[Any]],
    *,
    wait_for_focused: bool = True,
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,
) -> None:
    """Wait for the expected screen to be active."""

    async def wait_for_everything() -> None:
        await _wait_for_screen_change(pilot, expected_screen)
        if wait_for_focused:
            await _wait_for_focus(pilot)

    app = pilot.app

    try:
        await asyncio.wait_for(wait_for_everything(), timeout=timeout)
    except TimeoutError:
        wait_for_focused_info = " or nothing was focused " if wait_for_focused else " "
        raise AssertionError(
            f"Screen didn't changed to '{expected_screen}'{wait_for_focused_info}in {timeout=}s.\n"
            f"Current screen is: {app.screen}\n"
            f"Currently focused: {app.focused}"
        ) from None


async def wait_for_focus(
    pilot: ClivePilot,
    *,
    different_than: Widget | None = None,
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,
) -> None:
    """See _wait_for_focus."""
    try:
        task = _wait_for_focus(pilot, different_than=different_than)
        await asyncio.wait_for(task, timeout=timeout)
    except TimeoutError:
        wait_for_focused_info = "or focus not changed " if different_than else " "
        raise AssertionError(
            f"Nothing was focused {wait_for_focused_info}in {timeout=}s.\n"
            f"Current screen is: {pilot.app.screen}\n"
            f"Currently focused: {pilot.app.focused}"
        ) from None


async def focus_next(pilot: ClivePilot, timeout: float = TUI_TESTS_GENERAL_TIMEOUT) -> None:
    """Change focus to the next Widget (waits until something new is focused)."""
    await press_and_wait_for_focus(pilot, "tab", timeout=timeout)
