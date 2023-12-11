from __future__ import annotations

import re
from asyncio import sleep
from typing import TYPE_CHECKING

import test_tools as tt
from textual.css.query import NoMatches

if TYPE_CHECKING:
    from textual.app import App
    from textual.pilot import Pilot


TRANSACTION_ID_RE_PAT = re.compile(r"Transaction_id: (?P<transaction_id>[0-9a-z]+)")


async def write_text(pilot: Pilot[int], text: str) -> None:
    """Useful for place text in any Input widget."""
    await pilot.press(*list(text))


def is_key_binding_active(app: App[int], key: str, description: str) -> bool:
    """Check if key binding is active."""
    tt.logger.debug(f"Current active bindings: {app.namespace_bindings}")
    binding = app.namespace_bindings.get(key)
    return binding is not None and binding[1].description == description


async def get_notification_transaction_id(pilot: Pilot[int]) -> str:
    for notification in pilot.app._notifications:
        result = TRANSACTION_ID_RE_PAT.search(notification.message)
        transaction_id = result.group("transaction_id")  # type: ignore
        tt.logger.debug(f"transaction_id: '{transaction_id}'")

    for _ in range(3):
        try:
            toast = pilot.app.query_one("Toast")
        except NoMatches:
            tt.logger.debug("no toast")
            await pilot.pause()
            await sleep(0.5)
            continue
        tt.logger.debug(f"get_notification_transaction_id toast: {toast.renderable}")  # type: ignore
        break

    return transaction_id
