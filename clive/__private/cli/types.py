from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import TypeVar

    from clive.__private.models.schemas import AccountName, AccountUpdate2Operation, Authority, PublicKey

    AccountUpdateFunction = Callable[[AccountUpdate2Operation], AccountUpdate2Operation]
    AuthorityUpdateFunction = Callable[[Authority], Authority]
    AccountOrKeyT = TypeVar("AccountOrKeyT", AccountName, PublicKey)
