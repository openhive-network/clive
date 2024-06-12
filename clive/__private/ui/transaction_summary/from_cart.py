from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.transaction_summary.common import TransactionSummaryCommon

if TYPE_CHECKING:
    from clive.models import Transaction


class TransactionSummaryFromCart(TransactionSummaryCommon):
    SUBTITLE = "Built from cart"

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_transaction(self) -> Transaction:
        return await self.__build_transaction()

    async def __build_transaction(self) -> Transaction:
        return (
            await self.app.world.commands.build_transaction(content=self.app.world.profile_data.cart)
        ).result_or_raise

    def _actions_after_successful_broadcast(self) -> None:
        self.__clear_cart()

    def __clear_cart(self) -> None:
        self.app.world.profile_data.cart.clear()
