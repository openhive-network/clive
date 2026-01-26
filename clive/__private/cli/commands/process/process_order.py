from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import (
    OrderInvalidExpirationError,
    OrderMissingPriceSpecificationError,
    OrderMutuallyExclusiveOptionsError,
    OrderSameAssetError,
)
from clive.__private.models.schemas import (
    HbdExchangeRate,
    HiveDateTime,
    LimitOrderCancelOperation,
    LimitOrderCreate2Operation,
    LimitOrderCreateOperation,
)

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.core.commands.data_retrieval.order_data import OrderData
    from clive.__private.models.asset import Asset

# Default expiration is 28 days from now
DEFAULT_EXPIRATION_DAYS = 28


@dataclass(kw_only=True)
class ProcessOrderCreate(OperationCommand):
    from_account: str
    amount_to_sell: Asset.LiquidT
    min_to_receive: Asset.LiquidT | None = None
    price: Decimal | None = None
    order_id: int | None = None
    expiration: datetime | None = None
    fill_or_kill: bool = False

    @property
    def order_id_ensure(self) -> int:
        assert self.order_id is not None, "order_id should be set at this point"
        return self.order_id

    @property
    def expiration_ensure(self) -> datetime:
        assert self.expiration is not None, "expiration should be set at this point"
        return self.expiration

    @property
    def min_to_receive_ensure(self) -> Asset.LiquidT:
        assert self.min_to_receive is not None, "min_to_receive should be set at this point"
        return self.min_to_receive

    async def validate(self) -> None:
        self._validate_price_specification()
        await super().validate()

    def _validate_price_specification(self) -> None:
        """Validate that exactly one of min_to_receive or price is specified."""
        if self.min_to_receive is not None and self.price is not None:
            raise OrderMutuallyExclusiveOptionsError
        if self.min_to_receive is None and self.price is None:
            raise OrderMissingPriceSpecificationError

    async def _validate_expiration_against_head_block_time(self, head_block_time: datetime) -> None:
        """Validate that expiration is in the future relative to head_block_time."""
        if self.expiration is not None:
            expiration = self.expiration
            if expiration.tzinfo is None:
                expiration = expiration.replace(tzinfo=UTC)
            if expiration <= head_block_time:
                raise OrderInvalidExpirationError("Expiration must be in the future.")

    def _validate_assets(self) -> None:
        """Validate that amount_to_sell and min_to_receive are different asset types."""
        from clive.__private.models.asset import Asset  # noqa: PLC0415

        sell_is_hive = isinstance(self.amount_to_sell, Asset.Hive)
        receive_is_hive = isinstance(self.min_to_receive_ensure, Asset.Hive)

        if sell_is_hive == receive_is_hive:
            raise OrderSameAssetError

    def _get_min_to_receive_from_price(self) -> Asset.LiquidT:
        """Calculate and return min_to_receive from amount_to_sell and price."""
        from clive.__private.models.asset import Asset  # noqa: PLC0415

        assert self.price is not None, "price should be set at this point"

        amount = Decimal(str(self.amount_to_sell.amount))
        calculated_amount = amount * self.price

        # Determine the opposite asset type
        if isinstance(self.amount_to_sell, Asset.Hive):
            # Selling HIVE, receiving HBD
            return Asset.hbd(calculated_amount)
        # Selling HBD, receiving HIVE
        return Asset.hive(calculated_amount)

    async def fetch_data(self) -> None:
        await super().fetch_data()

        # Validate assets only when --min-to-receive is specified (not --price)
        # For --price path, the opposite asset type is implicit (HIVE→HBD or HBD→HIVE)
        if self.min_to_receive is not None:
            self._validate_assets()

        # Get head_block_time from node for expiration calculations
        dgpo = await self.world.node.api.database_api.get_dynamic_global_properties()
        head_block_time = dgpo.time

        # Validate user-provided expiration against head_block_time
        await self._validate_expiration_against_head_block_time(head_block_time)

        # Set default expiration if not specified
        # Use head_block_time from the node as reference to ensure expiration is valid
        if self.expiration is None:
            self.expiration = head_block_time + timedelta(days=DEFAULT_EXPIRATION_DAYS)

        # Auto-generate order_id if not specified
        if self.order_id is None:
            wrapper = await self.world.commands.retrieve_order_data(account_name=self.from_account)
            order_data: OrderData = wrapper.result_or_raise
            self.order_id = order_data.create_order_id()

    async def _create_operations(self) -> ComposeTransaction:
        if self.price is not None:
            # User provided --price → use LimitOrderCreate2Operation
            min_to_receive = self._get_min_to_receive_from_price()
            yield LimitOrderCreate2Operation(
                owner=self.from_account,
                orderid=self.order_id_ensure,
                amount_to_sell=self.amount_to_sell,
                exchange_rate=HbdExchangeRate(
                    base=self.amount_to_sell,
                    quote=min_to_receive,
                ),
                fill_or_kill=self.fill_or_kill,
                expiration=HiveDateTime(self.expiration_ensure),
            )
        else:
            # User provided --min-to-receive → use LimitOrderCreateOperation
            yield LimitOrderCreateOperation(
                owner=self.from_account,
                orderid=self.order_id_ensure,
                amount_to_sell=self.amount_to_sell,
                min_to_receive=self.min_to_receive_ensure,
                fill_or_kill=self.fill_or_kill,
                expiration=HiveDateTime(self.expiration_ensure),
            )


@dataclass(kw_only=True)
class ProcessOrderCancel(OperationCommand):
    from_account: str
    order_id: int

    async def _create_operations(self) -> ComposeTransaction:
        yield LimitOrderCancelOperation(
            owner=self.from_account,
            orderid=self.order_id,
        )
