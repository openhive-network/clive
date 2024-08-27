from __future__ import annotations

from clive.__private.core.node.api.api import Api
from clive.__private.models.schemas import (  # noqa: TCH001
    FindRcAccounts,
    GetResourcePool,
    ListRcAccounts,
    ListRcDirectDelegations,
    ResourceParams,
)


class RcApi(Api):
    @Api.method
    async def find_rc_accounts(self, *, accounts: list[str], refresh_mana: bool = False) -> FindRcAccounts:
        raise NotImplementedError

    @Api.method
    async def get_resource_params(self) -> ResourceParams:
        raise NotImplementedError

    @Api.method
    async def get_resource_pool(self) -> GetResourcePool:
        raise NotImplementedError

    @Api.method
    async def list_rc_accounts(self, *, accounts: list[str], refresh_mana: bool = False) -> ListRcAccounts:
        raise NotImplementedError

    @Api.method
    async def list_rc_direct_delegations(self, *, start: tuple[str, str], limit: int) -> ListRcDirectDelegations:
        raise NotImplementedError
