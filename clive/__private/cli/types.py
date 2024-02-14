from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import TypeVar

    from schemas.fields.basic import AccountName, PublicKey
    from schemas.fields.compound import Authority
    from schemas.operations import AccountUpdate2Operation

    AccountUpdateFunction = Callable[[AccountUpdate2Operation], AccountUpdate2Operation]
    AuthorityUpdateFunction = Callable[[Authority], Authority]
    AccountOrKeyT = TypeVar("AccountOrKeyT", AccountName, PublicKey)


AuthorityType = Literal["owner", "active", "posting"]
