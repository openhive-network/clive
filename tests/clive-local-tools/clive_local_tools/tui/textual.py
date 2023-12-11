from __future__ import annotations

import re
from typing import TYPE_CHECKING

import test_tools as tt
from textual.css.query import NoMatches

if TYPE_CHECKING:
    from textual.app import App
    from textual.pilot import Pilot
    from textual.widget import Widget


TRANSACTION_ID_RE_PAT = re.compile(r"Transaction with ID '(?P<transaction_id>[0-9a-z]+)'")


async def write_text(pilot: Pilot[int], text: str) -> None:
    """Useful for place text in any Input widget."""
    await pilot.press(*list(text))


def is_key_binding_active(app: App[int], key: str, description: str) -> bool:
    """Check if key binding is active."""
    tt.logger.debug(f"Current active bindings: {app.namespace_bindings}")
    binding = app.namespace_bindings.get(key)
    return binding is not None and binding[1].description == description


async def get_notification_transaction_id(pilot: Pilot[int]) -> str:
    try:
        toast: Widget = pilot.app.query_one("Toast")
    except NoMatches as error:
        raise AssertionError("Toast couldn't be found.") from error
    tt.logger.debug(f"get_notification_transaction_id toast: {toast.render()}")
    result = TRANSACTION_ID_RE_PAT.search(str(toast.render()))
    assert type(result) == re.Match, f"Expected 're.Match' type, current is {type(result)}."
    transaction_id = result.group("transaction_id")
    tt.logger.debug(f"transaction_id: '{transaction_id}'")

    return transaction_id
