from __future__ import annotations

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
    toasts = pilot.app.query(Toast)
    contents = [str(toast.render()) for toast in toasts]

    transaction_id = ""
    for content in contents:
        result = TRANSACTION_ID_RE_PAT.search(content)
        if result is not None:
            transaction_id = result.group("transaction_id")

    message = f"Toast notification containing the transaction ID couldn't be found. Current toasts are: {contents}"
    assert transaction_id, message
    return transaction_id
