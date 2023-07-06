from __future__ import annotations

import re
from typing import TypeAlias

from clive.__private.core.decimal_conventer import DecimalConverter
from clive.exceptions import CliveError
from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26, AssetHiveHF26, AssetVestsHF26


class AssetError(CliveError):
    """Base class for all asset related errors."""


class AssetLegacyInvalidFormatError(CliveError):
    def __init__(self, value: str) -> None:
        super().__init__(f"Invalid asset format: {value}")


class Asset:
    HIVE: TypeAlias = AssetHiveHF26
    HBD: TypeAlias = AssetHbdHF26
    VESTS: TypeAlias = AssetVestsHF26
    ANY: TypeAlias = HIVE | HBD | VESTS

    @classmethod
    def hive(cls, amount: float) -> Asset.HIVE:
        return Asset.HIVE(amount=cls.float_to_nai_int(amount, Asset.HIVE))

    @classmethod
    def hbd(cls, amount: float) -> Asset.HBD:
        return Asset.HBD(amount=cls.float_to_nai_int(amount, Asset.HBD))

    @classmethod
    def vests(cls, amount: float) -> Asset.VESTS:
        return Asset.VESTS(amount=cls.float_to_nai_int(amount, Asset.VESTS))

    @classmethod
    def float_to_nai_int(cls, number: float, asset_type: type[Asset.ANY]) -> int:
        result = number * (10 ** asset_type.get_asset_information().precision)
        assert result == int(result), "invalid precision"
        return int(result)

    @classmethod
    def resolve_symbol(cls, symbol: str) -> type[Asset.ANY]:
        match symbol:
            case "HIVE" | "TESTS":
                return Asset.HIVE
            case "HBD" | "TBD":
                return Asset.HBD
            case "VESTS":
                return Asset.VESTS
            case _:
                raise ValueError(f"Unknown asset type: '{symbol}'")

    @classmethod
    def from_legacy(cls, value: str) -> Asset.ANY:
        match = re.match(r"(\d+(?:\.\d+)?)\s*(\w+)", value)
        if not match:
            raise AssetLegacyInvalidFormatError(value)

        amount, symbol = match.groups()

        asset_cls = cls.resolve_symbol(symbol)
        asset_precision = asset_cls.get_asset_information().precision
        return asset_cls(amount=cls.__convert_amount_to_internal_representation(amount, asset_precision))

    @classmethod
    def to_legacy(cls, asset: Asset.ANY) -> str:
        return f"{cls.pretty_amount(asset)} {asset.get_asset_information().symbol[0]}"

    @classmethod
    def pretty_amount(cls, asset: Asset.ANY) -> str:
        return f"{int(asset.amount) / 10**asset.precision :.{asset.precision}f}"

    @staticmethod
    def __convert_amount_to_internal_representation(amount: str, precision: int) -> int:
        amount_decimal = DecimalConverter.convert(amount, precision=precision)
        return int(amount_decimal * 10**precision)
