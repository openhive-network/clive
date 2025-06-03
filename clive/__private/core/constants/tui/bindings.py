from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from textual.binding import Keymap

APP_QUIT_KEY_BINDING: Final[str] = "ctrl+q"
NEXT_SCREEN_BINDING_KEY: Final[str] = "ctrl+n"
PREVIOUS_SCREEN_BINDING_KEY: Final[str] = "ctrl+p"
FINALIZE_TRANSACTION_BINDING_KEY: Final[str] = "f"
SAVE_TRANSACTION_TO_FILE_BINDING_KEY: Final[str] = "s"
ADD_OPERATION_TO_CART_BINDING_KEY: Final[str] = "a"
BROADCAST_TRANSACTION_BINDING_KEY: Final[str] = "b"
LOAD_TRANSACTION_FROM_FILE_BINDING_KEY: Final[str] = "o"
REFRESH_TRANSACTION_METADATA_BINDING_KEY: Final[str] = "u"

KEYMAP: Keymap = MappingProxyType(
    {
        "app_quit": "ctrl+q",
        "next_screen": "ctrl+n",
        "previous_screen": "ctrl+p",
        "finalize_transaction": "f",
        "save_transaction_to_file": "s",
        "add_operation_to_cart": "a",
        "broadcast_transaction": "b",
        "load_transaction_from_file": "o",
        "refresh_transaction_metadata": "u",
    }
)
