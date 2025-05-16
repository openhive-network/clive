from __future__ import annotations

from typing import Final

from clive.__private.core.types import BindingIdKey

OPERATIONS: Final[BindingIdKey] = BindingIdKey("operations", "o")
SWITCH_WORKING_ACCOUNT: Final[BindingIdKey] = BindingIdKey("switch_working_account", "w")
ADD_ACCOUNT: Final[BindingIdKey] = BindingIdKey("add_account", "a")
DETAILS: Final[BindingIdKey] = BindingIdKey("details", "d")
REMOVE: Final[BindingIdKey] = BindingIdKey("remove_account", "r")
