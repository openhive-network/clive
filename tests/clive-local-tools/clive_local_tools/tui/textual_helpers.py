from __future__ import annotations

import asyncio
import math
from typing import TYPE_CHECKING, Any

from clive.__private.ui.screens.dashboard import Dashboard
from clive_local_tools.tui.checkers import assert_is_key_binding_active
from clive_local_tools.tui.constants import TUI_TESTS_GENERAL_TIMEOUT
from clive_local_tools.waiters import wait_for

if TYPE_CHECKING:
    from textual.screen import Screen
    from textual.widget import Widget

    from clive_local_tools.tui.types import ClivePilot


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
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,  # noqa: ASYNC109
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
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,  # noqa: ASYNC109
) -> None:
    """Press some binding and ensure focus changed after some action."""
    current_focus = pilot.app.focused
    await press_binding(pilot, key, key_description)
    await wait_for_focus(pilot, different_than=current_focus, timeout=timeout)


async def wait_for_accounts_data(pilot: ClivePilot, timeout: float = TUI_TESTS_GENERAL_TIMEOUT) -> None:  # noqa: ASYNC109
    """Wait for accounts node and alarms data to be available."""

    def is_data_available() -> bool:
        accounts = pilot.app.world.profile.accounts
        return accounts.is_tracked_accounts_node_data_available and accounts.is_tracked_accounts_alarms_data_available

    await wait_for(
        condition=is_data_available,
        message="Accounts node/alarms data hasn't arrived",
        timeout=timeout,
    )


async def wait_for_screen(
    pilot: ClivePilot,
    expected_screen: type[Screen[Any]],
    *,
    wait_for_focused: bool = True,
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,  # noqa: ASYNC109
) -> None:
    """Wait for the expected screen to be active."""
    app = pilot.app
    no_timeout = math.inf  # outer asyncio.timeout controls the actual timeout

    def is_expected_screen() -> bool:
        return isinstance(app.screen, expected_screen)

    def error_message() -> str:
        wait_for_focused_info = " or nothing was focused " if wait_for_focused else " "
        return (
            f"Screen didn't changed to '{expected_screen}'{wait_for_focused_info}in {timeout=}s.\n"
            f"Current screen is: {app.screen}\n"
            f"Currently focused: {app.focused}"
        )

    try:
        async with asyncio.timeout(timeout):
            await wait_for(
                condition=is_expected_screen,
                message=error_message,
                timeout=no_timeout,
            )
            if wait_for_focused:
                await wait_for_focus(pilot, timeout=no_timeout)
    except TimeoutError:
        raise AssertionError(error_message()) from None


async def wait_for_focus(
    pilot: ClivePilot,
    *,
    different_than: Widget | None = None,
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,  # noqa: ASYNC109
) -> None:
    """Wait for focus to be set or changed."""

    def is_focused() -> bool:
        app = pilot.app
        return bool(app.focused) and app.focused is not different_than

    def error_message() -> str:
        wait_for_focused_info = "or focus not changed " if different_than else ""
        return (
            f"Nothing was focused {wait_for_focused_info}in {timeout=}s.\n"
            f"Current screen is: {pilot.app.screen}\n"
            f"Currently focused: {pilot.app.focused}"
        )

    await wait_for(
        condition=is_focused,
        message=error_message,
        timeout=timeout,
    )


async def wait_for_cart_not_empty(pilot: ClivePilot, timeout: float = TUI_TESTS_GENERAL_TIMEOUT) -> None:  # noqa: ASYNC109
    """Wait for the transaction cart to have at least one operation."""
    await wait_for(
        condition=lambda: bool(pilot.app.world.profile.transaction),
        message="Cart is still empty",
        timeout=timeout,
    )


async def focus_next(pilot: ClivePilot, timeout: float = TUI_TESTS_GENERAL_TIMEOUT) -> None:  # noqa: ASYNC109
    """Change focus to the next Widget (waits until something new is focused)."""
    await press_and_wait_for_focus(pilot, "tab", timeout=timeout)


async def focus_prev(pilot: ClivePilot, timeout: float = TUI_TESTS_GENERAL_TIMEOUT) -> None:  # noqa: ASYNC109
    """Change focus to the previous Widget (waits until something new is focused)."""
    await press_and_wait_for_focus(pilot, "shift+tab", timeout=timeout)
