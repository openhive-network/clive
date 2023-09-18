from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.node.api.api import Api

if TYPE_CHECKING:
    from schemas.apis import reputation_api


class ReputationApi(Api):
    @Api.method
    async def get_account_reputations(
        self, *, account_lower_bound: str, limit: int = 1_000
    ) -> reputation_api.GetAccountReputations:
        raise NotImplementedError
