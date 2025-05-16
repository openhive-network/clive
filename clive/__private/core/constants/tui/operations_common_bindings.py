from __future__ import annotations

from typing import Final

from clive.__private.core.types import BindingIdKey

ADD_OPERATION_TO_CART: Final[BindingIdKey] = BindingIdKey("add_to_cart", "a")
FINALIZE_TRANSACTION: Final[BindingIdKey] = BindingIdKey("finalize_transaction", "f")
