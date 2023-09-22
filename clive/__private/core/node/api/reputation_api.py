from __future__ import annotations

from clive.__private.core.node.api.api import Api
from schemas.apis import reputation_api  # noqa: TCH001


class ReputationApi(Api):
    @Api.method
    async def get_account_reputations(
        self, *, account_lower_bound: str, limit: int = 1_000
    ) -> reputation_api.GetAccountReputations:
        raise NotImplementedError
