from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.models.schemas import AccountUpdate2Operation, Authority

    AccountUpdateFunction = Callable[[AccountUpdate2Operation], AccountUpdate2Operation]
    AuthorityUpdateFunction = Callable[[Authority], Authority]

    type AccountWithWeight = tuple[str, int]
    type KeyWithWeight = tuple[PublicKey, int]


AuthorityType = Literal["owner", "active", "posting"]
