from __future__ import annotations

from clive.__private.core.node.api.api import Api
from clive.__private.models.schemas import GetAccountReputations  # noqa: TCH001


class ReputationApi(Api):
    @Api.method
    async def get_account_reputations(self, *, account_lower_bound: str, limit: int = 1_000) -> GetAccountReputations:
        raise NotImplementedError
