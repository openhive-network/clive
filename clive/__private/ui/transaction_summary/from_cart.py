from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.transaction_summary.common import TransactionSummaryCommon

if TYPE_CHECKING:
    from rich.console import RenderableType

    from clive.models import Operation, Transaction


class TransactionSummaryFromCart(TransactionSummaryCommon):
    def __init__(self) -> None:
        super().__init__()

    def _get_subtitle(self) -> RenderableType:
        return "(Built from cart)"

    def _get_operations(self) -> list[Operation]:
        return list(self.app.world.profile_data.cart)

    async def _get_transaction(self) -> Transaction:
        return await self.__build_transaction()

    async def __build_transaction(self) -> Transaction:
        return (
            await self.app.world.commands.build_transaction(operations=self.app.world.profile_data.cart)
        ).result_or_raise

    def _actions_after_successful_broadcast(self) -> None:
        self.__clear_cart()

    def __clear_cart(self) -> None:
        self.app.world.profile_data.cart.clear()
