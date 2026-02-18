from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Final

import beekeepy.exceptions as bke

from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.exceptions import RequestIdError

if TYPE_CHECKING:
    from datetime import datetime

    from clive.__private.core.node import Node
    from clive.__private.models.asset import Asset
    from schemas.apis.database_api import FindLimitOrders
    from schemas.apis.database_api.fundaments_of_reponses import LimitOrdersFundament


@dataclass
class HarvestedDataRaw:
    orders: FindLimitOrders | None = None


@dataclass
class SanitizedData:
    orders: list[LimitOrdersFundament]


@dataclass
class OrderInfo:
    """Processed limit order information."""

    id_: int
    orderid: int
    seller: str
    created: datetime
    expiration: datetime
    remaining_sell_asset: Asset.LiquidT
    remaining_receive_asset: Asset.LiquidT
    price: Decimal

    @classmethod
    def from_fundament(cls, fundament: LimitOrdersFundament) -> OrderInfo:
        """Create OrderInfo from a LimitOrdersFundament."""
        from clive.__private.models.asset import Asset  # noqa: PLC0415

        # Parse sell_price to get the assets
        sell_price = fundament.sell_price
        base = sell_price.base
        quote = sell_price.quote

        # Calculate price: how much of quote you get per unit of base
        base_amount = Decimal(str(base.amount))
        quote_amount = Decimal(str(quote.amount))
        price = quote_amount / base_amount if base_amount != 0 else Decimal(0)

        # Current remaining amount to sell (for_sale is raw internal amount)
        remaining_amount = fundament.for_sale
        if isinstance(base, Asset.Hive):
            remaining_sell_asset: Asset.LiquidT = Asset.Hive(amount=remaining_amount)
        else:
            remaining_sell_asset = Asset.Hbd(amount=remaining_amount)

        # Proportionally calculate remaining receive amount
        ratio = Decimal(remaining_amount) / base_amount if base_amount != 0 else Decimal(0)
        receive_amount = round(quote_amount * ratio)
        if isinstance(quote, Asset.Hive):
            remaining_receive_asset: Asset.LiquidT = Asset.Hive(amount=receive_amount)
        else:
            remaining_receive_asset = Asset.Hbd(amount=receive_amount)

        return cls(
            id_=fundament.id_,
            orderid=fundament.orderid,
            seller=fundament.seller,
            created=fundament.created,
            expiration=fundament.expiration,
            remaining_sell_asset=remaining_sell_asset,
            remaining_receive_asset=remaining_receive_asset,
            price=price,
        )


@dataclass
class OrderData:
    orders: list[OrderInfo]

    def create_order_id(self) -> int:
        """
        Calculate the next available order id for LimitOrderCreateOperation.

        Raises:
            RequestIdError: If the maximum number of order ids is exceeded.

        Returns:
            The next available order id.
        """
        max_number_of_order_ids: Final[int] = 100

        existing_ids = [o.orderid for o in self.orders]
        if not existing_ids:
            return 0

        if len(existing_ids) >= max_number_of_order_ids:
            raise RequestIdError("Maximum quantity of order ids is 100")

        last_occupied_id = max(existing_ids)
        return last_occupied_id + 1


@dataclass(kw_only=True)
class OrderDataRetrieval(CommandDataRetrieval[HarvestedDataRaw, SanitizedData, OrderData]):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> HarvestedDataRaw:
        async with await self.node.batch() as node:
            return HarvestedDataRaw(
                await node.api.database_api.find_limit_orders(account=self.account_name),
            )
        raise bke.UnknownDecisionPathError(f"{self.__class__.__name__}:_harvest_data_from_api")

    async def _sanitize_data(self, data: HarvestedDataRaw) -> SanitizedData:
        return SanitizedData(
            orders=self.__assert_orders(data.orders),
        )

    async def _process_data(self, data: SanitizedData) -> OrderData:
        orders = [OrderInfo.from_fundament(order) for order in data.orders]
        return OrderData(orders=orders)

    def __assert_orders(self, data: FindLimitOrders | None) -> list[LimitOrdersFundament]:
        assert data is not None, "FindLimitOrders data is missing"
        return data.orders
