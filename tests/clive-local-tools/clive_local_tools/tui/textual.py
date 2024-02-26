from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING, Final

import test_tools as tt
from textual.widgets._toast import Toast

if TYPE_CHECKING:
    from textual.app import App
    from textual.pilot import Pilot


TRANSACTION_ID_RE_PAT: Final[re.Pattern[str]] = re.compile(r"Transaction with ID '(?P<transaction_id>[0-9a-z]+)'")


async def write_text(pilot: Pilot[int], text: str) -> None:
    """Useful for place text in any Input widget."""
    await pilot.press(*list(text))


async def key_press(pilot: Pilot[int], *keys: str) -> None:
    """Safer version of Pilot.press."""
    for key in keys:
        await pilot.press(key)


def is_key_binding_active(app: App[int], key: str, description: str) -> bool:
    """Check if key binding is active."""
    tt.logger.debug(f"Current active bindings: {app.namespace_bindings}")
    binding = app.namespace_bindings.get(key)
    return binding is not None and binding[1].description == description


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
        tt.logger.debug(f"Toasts:\n{contents}")

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
