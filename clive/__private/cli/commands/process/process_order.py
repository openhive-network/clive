from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import (
    OrderExpirationNotInFutureError,
    OrderExpirationTooFarInFutureError,
    OrderFillOrKillNotFilledError,
    OrderMissingPriceSpecificationError,
    OrderMutuallyExclusiveOptionsError,
    OrderSameAssetError,
)
from clive.__private.cli.warnings import typer_echo_warnings
from clive.__private.core.error_handlers.abc.error_notificator import CannotNotifyError
from clive.__private.models.schemas import (
    HbdExchangeRate,
    HiveDateTime,
    LimitOrderCancelOperation,
    LimitOrderCreate2Operation,
    LimitOrderCreateOperation,
)

if TYPE_CHECKING:
    from decimal import Decimal

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
    expiration: datetime | timedelta | None = None
    fill_or_kill: bool = False
    _head_block_time: datetime | None = None

    @property
    def order_id_ensure(self) -> int:
        assert self.order_id is not None, "order_id should be set at this point"
        return self.order_id

    @property
    def expiration_ensure(self) -> datetime:
        assert isinstance(self.expiration, datetime), "expiration should be resolved to datetime at this point"
        return self.expiration

    @property
    def min_to_receive_ensure(self) -> Asset.LiquidT:
        assert self.min_to_receive is not None, "min_to_receive should be set at this point"
        return self.min_to_receive

    async def validate(self) -> None:
        self._validate_price_specification()
        if self.min_to_receive is not None:
            self._validate_assets()
        await super().validate()

    def _validate_price_specification(self) -> None:
        """Validate that exactly one of min_to_receive or price is specified."""
        if self.min_to_receive is not None and self.price is not None:
            raise OrderMutuallyExclusiveOptionsError
        if self.min_to_receive is None and self.price is None:
            raise OrderMissingPriceSpecificationError

    async def _validate_expiration_against_head_block_time(self) -> None:
        """Validate that expiration is in the future relative to head_block_time."""
        assert self._head_block_time is not None, "head_block_time should be set at this point"
        expiration = self.expiration
        assert isinstance(expiration, datetime), "expiration should be resolved to datetime at this point"
        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=UTC)
        if expiration <= self._head_block_time:
            raise OrderExpirationNotInFutureError
        if expiration > self._head_block_time + timedelta(days=DEFAULT_EXPIRATION_DAYS):
            raise OrderExpirationTooFarInFutureError

    def _validate_assets(self) -> None:
        """Validate that amount_to_sell and min_to_receive are different asset types."""
        from clive.__private.models.asset import Asset  # noqa: PLC0415

        sell_is_hive = isinstance(self.amount_to_sell, Asset.Hive)
        receive_is_hive = isinstance(self.min_to_receive_ensure, Asset.Hive)

        if sell_is_hive == receive_is_hive:
            raise OrderSameAssetError

    def _get_min_to_receive_from_price(self) -> Asset.LiquidT:
        """Calculate and return min_to_receive from amount_to_sell and price (HBD per HIVE)."""
        from clive.__private.models.asset import Asset  # noqa: PLC0415

        assert self.price is not None, "price should be set at this point"

        amount = Asset.as_decimal(self.amount_to_sell)

        if isinstance(self.amount_to_sell, Asset.Hive):
            # Selling HIVE, receiving HBD: multiply by price (HBD per HIVE)
            return Asset.hbd(amount * self.price)
        # Selling HBD, receiving HIVE: divide by price (HBD per HIVE)
        return Asset.hive(amount / self.price)

    async def fetch_data(self) -> None:
        await super().fetch_data()

        # Get head_block_time from node for expiration calculations
        dgpo = await self.world.node.api.database_api.get_dynamic_global_properties()
        head_block_time = dgpo.time.replace(tzinfo=UTC)

        # Resolve relative timedelta to absolute datetime
        if isinstance(self.expiration, timedelta):
            self.expiration = head_block_time + self.expiration

        # Set default expiration if not specified
        # Use head_block_time from the node as reference to ensure expiration is valid
        if self.expiration is None:
            self.expiration = head_block_time + timedelta(days=DEFAULT_EXPIRATION_DAYS)

        self._head_block_time = head_block_time

        # Auto-generate order_id if not specified
        if self.order_id is None:
            wrapper = await self.world.commands.retrieve_order_data(account_name=self.from_account)
            order_data: OrderData = wrapper.result_or_raise
            self.order_id = order_data.create_order_id()

    async def validate_inside_context_manager(self) -> None:
        await super().validate_inside_context_manager()
        await self._validate_expiration_against_head_block_time()

    async def _run(self) -> None:
        try:
            await super()._run()
        except CannotNotifyError as error:
            if "Cancelling order because it was not filled" in error.reason:
                raise OrderFillOrKillNotFilledError from None
            raise

    async def _create_operations(self) -> ComposeTransaction:
        if self.price is not None:
            # User provided --price → use LimitOrderCreate2Operation
            with typer_echo_warnings():
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
