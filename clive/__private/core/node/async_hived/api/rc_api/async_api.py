from __future__ import annotations

from beekeepy.handle.remote import AbstractAsyncApi

from hiveio_api import rc_api


class RcApi(AbstractAsyncApi):
    api = AbstractAsyncApi.endpoint_jsonrpc

    @api
    async def find_rc_accounts(
        self, *, accounts: list[str], refresh_mana: bool = False
    ) -> rc_api.FindRcAccountsResponse:
        raise NotImplementedError

    @api
    async def get_resource_params(self) -> rc_api.GetResourceParamsResponse:
        raise NotImplementedError

    @api
    async def get_resource_pool(self) -> rc_api.GetResourcePoolResponse:
        raise NotImplementedError

    @api
    async def list_rc_accounts(
        self, *, accounts: list[str], refresh_mana: bool = False
    ) -> rc_api.ListRcAccountsResponse:
        raise NotImplementedError

    @api
    async def list_rc_direct_delegations(
        self, *, start: tuple[str, str], limit: int
    ) -> rc_api.ListRcDirectDelegationsResponse:
        raise NotImplementedError
