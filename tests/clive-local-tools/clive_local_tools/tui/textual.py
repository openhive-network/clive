from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING, Any, Final

import test_tools as tt
from textual.widgets._toast import Toast

from clive_local_tools.tui.checkers import assert_is_key_binding_active

if TYPE_CHECKING:
    from textual.pilot import Pilot
    from textual.screen import Screen

TRANSACTION_ID_RE_PAT: Final[re.Pattern[str]] = re.compile(r"Transaction with ID '(?P<transaction_id>[0-9a-z]+)'")


async def write_text(pilot: Pilot[int], text: str) -> None:
    """Useful for place text in any Input widget."""
    await pilot.press(*list(text))


async def press_binding(pilot: Pilot[int], key: str, key_description: str | None = None) -> None:
    """Safer version of pilot.press which ensures that the key binding is active and optionally asserts binding desc."""
    assert_is_key_binding_active(pilot.app, key, key_description)
    await pilot.press(key)


async def press_and_wait_for_screen(
    pilot: Pilot[int],
    key: str,
    expected_screen: type[Screen[Any]],
    *,
    key_description: str | None = None,
) -> None:
    """Press some binding and ensure screen changed after some action."""
    await press_binding(pilot, key, key_description)
    await wait_for_screen(pilot, expected_screen)


async def wait_for_screen(pilot: Pilot[int], expected_screen: type[Screen[Any]], *, timeout: float = 3.0) -> None:
    """Wait for the expected screen to be active."""

    async def wait_for_screen_change() -> None:
        while not isinstance(app.screen, expected_screen):
            await pilot.pause(0.1)

    app = pilot.app

    try:
        await asyncio.wait_for(wait_for_screen_change(), timeout=timeout)
    except asyncio.TimeoutError:
        raise AssertionError(
            f"Screen didn't changed to '{expected_screen}' in {timeout=}. Current one is: {app.screen}"
        ) from None


async def get_notification_transaction_id(pilot: Pilot[int]) -> str:
    """
    Will look for a toast notification containing the transaction ID and return it.

    If no toast notification is found, will raise an AssertionError. If more than one toast notification is found, will
    ignore the rest and return the transaction ID from the last one.
    """
    seconds_to_wait: Final[float] = 3.0

    async def look_for_transaction_id_in_toasts() -> str:
        toasts = pilot.app.query(Toast)
        contents = [str(toast.render()) for toast in toasts]

        transaction_id = ""
        for content in contents:
            result = TRANSACTION_ID_RE_PAT.search(content)
            if result is not None:
                transaction_id = result.group("transaction_id")
        return transaction_id

    async def wait_for_transaction_id_to_be_found() -> str:
        seconds_already_waited = 0.0
        pool_time = 0.1
        while True:
            transaction_id = await look_for_transaction_id_in_toasts()
            if transaction_id:
                return transaction_id
            tt.logger.info(
                "Didn't find the transaction ID in the toast notification. Already waited"
                f" {seconds_already_waited:.2f}s."
            )
            await asyncio.sleep(pool_time)
            seconds_already_waited += pool_time

    try:
        return await asyncio.wait_for(wait_for_transaction_id_to_be_found(), timeout=seconds_to_wait)
    except asyncio.TimeoutError:
        raise AssertionError(
            f"Toast notification containing the transaction ID couldn't be found. Waited {seconds_to_wait:.2f}s"
        ) from None
