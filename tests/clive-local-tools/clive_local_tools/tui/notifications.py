from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING, Final

import test_tools as tt
from textual.widgets._toast import Toast

from clive_local_tools.tui.constants import TUI_TESTS_GENERAL_TIMEOUT

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive_local_tools.tui.types import CliveApp, ClivePilot


async def extract_transaction_id_from_notification(pilot: ClivePilot) -> str:
    """
    Extract the transaction ID from the notification message.

    For more details see `extract_message_from_notification` docstring.
    """
    transaction_id_pattern: Final[re.Pattern[str]] = re.compile(r"Transaction with ID '(?P<transaction_id>[0-9a-z]+)'")

    def look_for_transaction_id_in_string(string: str) -> str:
        result = transaction_id_pattern.search(string)
        if result is not None:
            return result.group("transaction_id")
        return ""

    return await extract_message_from_notification(pilot, look_for_transaction_id_in_string)


async def extract_message_from_notification(
    pilot: ClivePilot,
    find_message_cb: Callable[[str], str],
    *,
    search_in_history: bool = True,
    timeout: float = TUI_TESTS_GENERAL_TIMEOUT,  # noqa: ASYNC109
) -> str:
    """
    Will look for a notification containing the expected message and returns it.

    First, will try to find the expected message in the toast notifications. If not found, and set to search in history,
    will look also in the notification history (as it may be already expired).

    Args:
    ----
    pilot: The ClivePilot instance.
    find_message_cb : The callback function to find the message within the notification content.
    search_in_history: If set to True, will also look for the message in the notification history.
    timeout: The maximum time to wait for the notification to appear.

    Returns:
    -------
    The message extracted from the notification.

    Raises:
    ------
    AssertionError: If the toast notification containing the expected message couldn't be found within the timeout.
    """
    app = pilot.app

    async def wait_for_message_to_be_found() -> str:
        seconds_already_waited = 0.0
        pool_time = 0.1
        first_try = True

        while True:
            transaction_id = _extract_message_from_toasts(app, find_message_cb)
            if search_in_history and first_try and not transaction_id:
                # If message wasn't found in the toast notification, check the notification history,
                # but only on the first try, so if notification arrives later, it will be found as in the toast.
                first_try = False
                tt.logger.info(
                    "Didn't found the expected message in the toast notification. Checking notification history..."
                )
                transaction_id = _extract_message_from_notifications_history(app, find_message_cb)

            if transaction_id:
                return transaction_id

            tt.logger.info(
                "Didn't found the expected message in the toast notification or notification history. Already waited"
                f" {seconds_already_waited:.2f}s."
            )
            await pilot.pause(pool_time)
            seconds_already_waited += pool_time

    try:
        return await asyncio.wait_for(wait_for_message_to_be_found(), timeout=timeout)
    except TimeoutError:
        raise AssertionError(
            f"Toast notification containing the transaction ID couldn't be found. Waited {timeout:.2f}s"
        ) from None


def _extract_message_from_toasts(app: CliveApp, find_message_cb: Callable[[str], str]) -> str:
    """
    Extract the message from currently present toast notifications.

    If more than one message is found, the most recent will be returned.

    Args:
    ----
    app: The CliveApp instance
    find_message_cb : The callback function to find the message within the notification content.

    Returns:
    -------
    The message extracted from the present toast notifications. Will return an empty string if no message was found.
    """
    toasts = app.screen.query(Toast)
    contents = [str(toast.render()) for toast in toasts]

    message = ""
    for content in contents:
        message = find_message_cb(content)
    return message


def _extract_message_from_notifications_history(app: CliveApp, find_message_cb: Callable[[str], str]) -> str:
    """
    Extract the message from notification history.

    If more than one message is found, the most recent will be returned.

    Args:
    ----
    app: The CliveApp instance
    find_message_cb : The callback function to find the message within the notification content.

    Returns:
    -------
    The message extracted from the notification history. Will return an empty string if no message was found.
    """
    message = ""
    for notification in app.notification_history:
        message = find_message_cb(notification.message)
    return message
