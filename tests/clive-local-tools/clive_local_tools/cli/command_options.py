from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import NotRequired, Required, TypedDict

if TYPE_CHECKING:
    import test_tools as tt


KwargsType = str | bool | None


class WorldWithoutBeekeeperKwargs(TypedDict):
    profile_name: NotRequired[str]
    use_beekeeper: NotRequired[bool]


class OperationCommonKwargs(TypedDict):
    profile_name: NotRequired[str]
    password: NotRequired[str]
    sign: NotRequired[bool]
    beekeeper_remote: NotRequired[str]
    broadcast: NotRequired[bool]
    save_file: NotRequired[str]


class TransferCommonKwargs(TypedDict):
    amount: Required[str]
    memo: NotRequired[str] = ""
    from_account: NotRequired[tt.Account]


class TransferKwargs(OperationCommonKwargs, TransferCommonKwargs): ...
