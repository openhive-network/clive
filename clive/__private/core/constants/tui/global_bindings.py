from __future__ import annotations

from typing import Final

from clive.__private.core.types import BindingIdKey

SHOW_HELP: Final[BindingIdKey] = BindingIdKey("show_help", "?,f1")
HIDE_HELP: Final[BindingIdKey] = BindingIdKey("hide_help", f"escape,q,{SHOW_HELP.key}")
SWITCH_MODE_INTO_LOCKED: Final[BindingIdKey] = BindingIdKey("lock", "ctrl+l")
GO_TO_DASHBOARD: Final[BindingIdKey] = BindingIdKey("dashboard", "ctrl+d")
GO_TO_TRANSACTION_SUMMARY: Final[BindingIdKey] = BindingIdKey("transaction_summary", "ctrl+t")
GO_TO_SWITCH_NODE: Final[BindingIdKey] = BindingIdKey("switch_node", "ctrl+n")
GO_TO_SETTINGS: Final[BindingIdKey] = BindingIdKey("settings", "ctrl+s")
CLEAR_NOTIFICATIONS: Final[BindingIdKey] = BindingIdKey("clear_notifications", "ctrl+x")
GO_TO_LOAD_TRANSACTION_FROM_FILE: Final[BindingIdKey] = BindingIdKey("open_transaction_from_file", "ctrl+o")
APP_QUIT: Final[BindingIdKey] = BindingIdKey("close_clive", "ctrl+q")
SCREENSHOT: Final[BindingIdKey] = BindingIdKey("screenshot", "ctrl+p")
