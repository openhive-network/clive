from __future__ import annotations

from typing import Final

from clive.__private.config import settings

TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT: Final[float] = settings.get("tests.tui_tests_patched_notification_timeout_secs")
TUI_TESTS_GENERAL_TIMEOUT: Final[float] = settings.get("tests.tui_tests_general_timeout_secs")
