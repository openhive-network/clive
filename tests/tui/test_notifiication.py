from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.tui.constants import TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.tui.types import ClivePilot


async def test_patched_notification_timeout(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    # ARRANGE
    notification_message = "test notification"
    _, _, pilot = prepared_tui_on_dashboard

    # ACT
    pilot.app.notify(notification_message)
    await pilot.pause()  # wait for notification

    notifications = iter(pilot.app._notifications)
    notification = next(notifications)
    if "mode" in notification.message:  # ignore the UNLOCKED mode notification
        notification = next(notifications)

    # ASSERT
    assert notification.message == notification_message, "Notification message differs from the expected"
    assert notification.timeout == TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT, "Notification timeout was not set correctly"
