from __future__ import annotations

from clive.__private.core.node.api.api import Api
from clive.models import Asset  # noqa: TCH001
from schemas import rc_api  # noqa: TCH001


class RcApi(Api):
    @Api.method
    def find_rc_accounts(self, accounts: list[str]) -> rc_api.FindRcAccounts[Asset.VESTS]:
        raise NotImplementedError()

    @Api.method
    def get_resource_params(self) -> rc_api.GetResourceParams:
        raise NotImplementedError()

    @Api.method
    def get_resource_pool(self) -> rc_api.GetResourcePool:
        raise NotImplementedError()

    @Api.method
    def list_rc_accounts(self, accounts: list[str]) -> rc_api.ListRcAccounts[Asset.VESTS]:
        raise NotImplementedError()

    @Api.method
    def list_rc_direct_delegations(self, start: tuple[str, str], limit: int) -> rc_api.ListRcDirectDelegations:
        raise NotImplementedError()
