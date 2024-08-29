from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.screens.transaction_summary.common import TransactionSummaryCommon

if TYPE_CHECKING:
    from clive.__private.models import Transaction


class TransactionSummaryFromCart(TransactionSummaryCommon):
    SUBTITLE = "Built from cart"

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_transaction(self) -> Transaction:
        return await self.__build_transaction()

    async def __build_transaction(self) -> Transaction:
        return (await self.commands.build_transaction(content=self.profile.cart)).result_or_raise

    def _actions_after_successful_broadcast(self) -> None:
        self.__clear_cart()

    def __clear_cart(self) -> None:
        self.profile.cart.clear()
