from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, ContextManager, Protocol

from clive_local_tools.data.models import WalletInfo

if TYPE_CHECKING:
    from collections.abc import Coroutine


Wallets = list[WalletInfo]


class SetupWalletsFactory(Protocol):
    def __call__(
        self, count: int, *, import_keys: bool = True, keys_per_wallet: int = 1
    ) -> Coroutine[Any, Any, list[WalletInfo]]: ...


EnvContextFactory = Callable[[str | None], ContextManager[None]]
GenericEnvContextFactory = Callable[[str], EnvContextFactory]
