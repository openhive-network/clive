from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from clive.__private.core.keys import PublicKey
    from clive.__private.models.schemas import AccountUpdate2Operation, Authority, OperationUnion

    AccountUpdateFunction = Callable[[AccountUpdate2Operation], AccountUpdate2Operation]
    AuthorityUpdateFunction = Callable[[Authority], Authority]
    type ComposeTransaction = AsyncGenerator[OperationUnion]

ACCOUNT_CREATION_SUBCOMMANDS = Literal["owner", "active", "posting", "memo"]

type KeyOrAccountWithWeight = tuple[str | PublicKey, int]
type AccountCreationPositionalArgument = ACCOUNT_CREATION_SUBCOMMANDS | KeyOrAccountWithWeight
