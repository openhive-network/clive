from __future__ import annotations

from clive.__private.core.node.api.api import Api
from clive.models import Asset  # noqa: TCH001
from schemas.apis import rc_api  # noqa: TCH001


class RcApi(Api):
    @Api.method
    async def find_rc_accounts(
        self, *, accounts: list[str], refresh_mana: bool = False
    ) -> rc_api.FindRcAccounts[Asset.Vests]:
        raise NotImplementedError

    @Api.method
    async def get_resource_params(self) -> rc_api.GetResourceParams:
        raise NotImplementedError

    @Api.method
    async def get_resource_pool(self) -> rc_api.GetResourcePool:
        raise NotImplementedError

    @Api.method
    async def list_rc_accounts(
        self, *, accounts: list[str], refresh_mana: bool = False
    ) -> rc_api.ListRcAccounts[Asset.Vests]:
        raise NotImplementedError

    @Api.method
    async def list_rc_direct_delegations(self, *, start: tuple[str, str], limit: int) -> rc_api.ListRcDirectDelegations:
        raise NotImplementedError
