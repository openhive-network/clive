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
    Hive: TypeAlias = AssetHiveHF26
    Hbd: TypeAlias = AssetHbdHF26
    Vests: TypeAlias = AssetVestsHF26
    AnyT: TypeAlias = Hive | Hbd | Vests

    @classmethod
    def hive(cls, amount: float) -> Asset.Hive:
        return Asset.Hive(amount=cls.float_to_nai_int(amount, Asset.Hive))

    @classmethod
    def hbd(cls, amount: float) -> Asset.Hbd:
        return Asset.Hbd(amount=cls.float_to_nai_int(amount, Asset.Hbd))

    @classmethod
    def vests(cls, amount: float) -> Asset.Vests:
        return Asset.Vests(amount=cls.float_to_nai_int(amount, Asset.Vests))

    @classmethod
    def float_to_nai_int(cls, number: float, asset_type: type[Asset.AnyT]) -> int:
        result = number * (10 ** asset_type.get_asset_information().precision)
        assert result == int(result), "invalid precision"
        return int(result)

    @classmethod
    def resolve_symbol(cls, symbol: str) -> type[Asset.AnyT]:
        match symbol:
            case "HIVE" | "TESTS":
                return Asset.Hive
            case "HBD" | "TBD":
                return Asset.Hbd
            case "VESTS":
                return Asset.Vests
            case _:
                raise ValueError(f"Unknown asset type: '{symbol}'")

    @classmethod
    def from_legacy(cls, value: str) -> Asset.AnyT:
        match = re.match(r"(\d+(?:\.\d+)?)\s*(\w+)", value)
        if not match:
            raise AssetLegacyInvalidFormatError(value)

        amount, symbol = match.groups()

        asset_cls = cls.resolve_symbol(symbol)
        asset_precision = asset_cls.get_asset_information().precision
        return asset_cls(amount=cls.__convert_amount_to_internal_representation(amount, asset_precision))

    @classmethod
    def to_legacy(cls, asset: Asset.AnyT) -> str:
        return f"{cls.pretty_amount(asset)} {asset.get_asset_information().symbol[0]}"

    @classmethod
    def pretty_amount(cls, asset: Asset.AnyT) -> str:
        return f"{int(asset.amount) / 10**asset.precision :.{asset.precision}f}"

    @staticmethod
    def __convert_amount_to_internal_representation(amount: str, precision: int) -> int:
        amount_decimal = DecimalConverter.convert(amount, precision=precision)
        return int(amount_decimal * 10**precision)
