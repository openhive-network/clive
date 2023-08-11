from __future__ import annotations

from clive.__private.core.node.api.api import Api
from schemas.account_history_api import response_schemas as account_history_api  # noqa: TCH001


class AccountHistoryApi(Api):
    @Api.method
    async def get_account_history(  # noqa: PLR0913
        self,
        account: str,
        start: int = -1,
        limit: int = 1_000,
        include_reversible: bool = True,
        operation_filter_low: int | None = None,
        operation_filter_high: int | None = None,
    ) -> account_history_api.GetAccountHistory:
        raise NotImplementedError

    @Api.method
    async def get_transaction(self, id_: str, include_reversible: bool = True) -> account_history_api.GetTransaction:
        raise NotImplementedError

    @Api.method
    async def enum_virtual_ops(  # noqa: PLR0913
        self,
        block_range_begin: int,
        block_range_end: int,
        operation_begin: int | None = None,
        filter_: int | None = None,
        limit: int | None = None,
        include_reversible: bool = True,
        group_by_block: bool = False,
    ) -> account_history_api.EnumVirtualOps:
        raise NotImplementedError

    async def get_ops_in_block(
        self, block_num: int, only_virtual: bool = False, include_reversible: bool = True
    ) -> account_history_api.GetOpsInBlock:
        raise NotImplementedError
