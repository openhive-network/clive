from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.models.schemas import AccountUpdate2Operation, Authority, OperationUnion

    AccountUpdateFunction = Callable[[AccountUpdate2Operation], AccountUpdate2Operation]
    AuthorityUpdateFunction = Callable[[Authority], Authority]
    type ComposeTransaction = AsyncGenerator[OperationUnion]

type KeyOrAccountWithWeight = tuple[str | PublicKey, int]
