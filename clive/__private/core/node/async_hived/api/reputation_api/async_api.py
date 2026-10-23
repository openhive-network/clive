from __future__ import annotations

from beekeepy.handle.remote import AbstractAsyncApi

from hiveio_api import reputation_api


class ReputationApi(AbstractAsyncApi):
    @AbstractAsyncApi.endpoint_jsonrpc
    async def get_account_reputations(
        self, *, account_lower_bound: str, limit: int = 1_000
    ) -> reputation_api.GetAccountReputationsResponse:
        raise NotImplementedError
