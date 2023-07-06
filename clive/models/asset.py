from __future__ import annotations

import re
from typing import ClassVar, Literal, TypeAlias

from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26, AssetHiveHF26, AssetVestsHF26


class Asset:
    HIVE: ClassVar[TypeAlias] = AssetHiveHF26
    HBD: ClassVar[TypeAlias] = AssetHbdHF26
    VESTS: ClassVar[TypeAlias] = AssetVestsHF26
    ANY: ClassVar[TypeAlias] = HIVE | HBD | VESTS
    ALLOWED_SYMBOLS: ClassVar[TypeAlias] = Literal["HIVE", "TESTS", "HBD", "TBD", "VESTS"]

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
    def resolve_symbol(cls, symbol: ALLOWED_SYMBOLS) -> Asset.ANY:
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
    def from_legacy(cls, legacy: str) -> Asset.ANY:
        legacy_parsing_regex = re.compile(r"(\d+\.\d+) ([A-Z]+)")
        parsed = legacy_parsing_regex.match(legacy)
        assert parsed is not None
        amount = int(parsed.group(1).replace(".", ""))
        symbol: Asset.ALLOWED_SYMBOLS = parsed.group(2)
        return cls.resolve_symbol(symbol)(amount=amount)

    @classmethod
    def to_legacy(cls, asset: Asset.ANY) -> str:
        return f"{cls.pretty_amount(asset)} {asset.get_asset_information().symbol[0]}"

    @classmethod
    def pretty_amount(cls, asset: Asset.ANY) -> str:
        return f"{int(asset.amount) / 10**asset.precision :.{asset.precision}f}"
