from __future__ import annotations

from typing import Final

from clive.__private.core.types import BindingIdKey

BROADCAST_TRANSACTION: Final[BindingIdKey] = BindingIdKey("broadcast", "b")
SAVE_TRANSACTION_TO_FILE: Final[BindingIdKey] = BindingIdKey("save_transaction_to_file", "s")
UPDATE_TRANSACTION_METADATA: Final[BindingIdKey] = BindingIdKey("update_metadata", "u")
JSON: Final[BindingIdKey] = BindingIdKey("json", "j")
REMOVE: Final[BindingIdKey] = BindingIdKey("remove_operation", "r")
