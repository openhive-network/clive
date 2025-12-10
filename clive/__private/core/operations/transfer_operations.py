"""Shared transfer operation creation logic."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from clive.__private.models.asset import Asset
from clive.__private.models.schemas import TransferOperation

if TYPE_CHECKING:
    pass


def create_transfer_operation(
    from_account: str,
    to_account: str,
    amount: str | Asset.LiquidT,
    memo: str = "",
) -> TransferOperation:
    """
    Create a transfer operation.

    Args:
        from_account: Account sending the transfer
        to_account: Account receiving the transfer
        amount: Amount to transfer (can be string like "1.000 HIVE" or Asset object)
        memo: Optional memo message

    Returns:
        TransferOperation ready to be added to a transaction
    """
    normalized_amount = _normalize_amount(amount)
    return TransferOperation(
        from_=from_account,
        to=to_account,
        amount=normalized_amount,
        memo=memo,
    )


def _normalize_amount(amount: str | Asset.LiquidT) -> Asset.LiquidT:
    """Convert amount to proper Asset.LiquidT type."""
    converted_amount = Asset.from_legacy(amount) if isinstance(amount, str) else amount
    assert not Asset.is_vests(
        converted_amount
    ), f"Invalid asset type. Given: {type(converted_amount)}, Needs: {Asset.LiquidT}"
    return cast("Asset.LiquidT", converted_amount)
