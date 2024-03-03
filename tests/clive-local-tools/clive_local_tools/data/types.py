from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from clive_local_tools.data.models import WalletInfo  # noqa: TCH001

if TYPE_CHECKING:
    from collections.abc import Coroutine


class WalletGeneratorT(Protocol):
    def __call__(
        self, *, import_keys: bool = True, keys_per_wallet: int = 1
    ) -> Coroutine[Any, Any, WalletInfo]: ...
