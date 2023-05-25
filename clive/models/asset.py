from __future__ import annotations

import re
from typing import Literal

from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26, AssetHiveHF26, AssetVestsHF26

AssetT = AssetHiveHF26 | AssetHbdHF26 | AssetVestsHF26


class Asset:
    @classmethod
    def hive(cls, amount: float) -> AssetHiveHF26:
        return AssetHiveHF26(amount=cls.float_to_nai_int(amount, AssetHiveHF26))

    @classmethod
    def hbd(cls, amount: float) -> AssetHbdHF26:
        return AssetHbdHF26(amount=cls.float_to_nai_int(amount, AssetHbdHF26))

    @classmethod
    def vests(cls, amount: float) -> AssetVestsHF26:
        return AssetVestsHF26(amount=cls.float_to_nai_int(amount, AssetVestsHF26))

    @classmethod
    def float_to_nai_int(cls, number: float, asset_type: type[AssetT]) -> int:
        result = number * (10 ** asset_type.get_asset_information().precision)
        assert result == int(result), "invalid precision"
        return int(result)

    @classmethod
    def resolve_symbol(cls, symbol: Literal["HIVE", "TESTS", "HBD", "TBD", "VESTS"] | str) -> type[AssetT]:
        match symbol:
            case ["HIVE", "TESTS"]:
                return AssetHiveHF26
            case ["HBD", "TBD"]:
                return AssetHbdHF26
            case "VESTS":
                return AssetVestsHF26
        raise ValueError(f"Unknown asset type: '{symbol}'")

    @classmethod
    def from_legacy(cls, legacy: str) -> AssetT:
        legacy_parsing_regex = re.compile(r"([0-9]+\.[0-9]+) ([A-Z]+)")
        parsed = legacy_parsing_regex.match(legacy)
        assert parsed is not None
        amount = int(parsed.group(1).replace(".", ""))
        symbol = parsed.group(2)
        return cls.resolve_symbol(symbol)(amount=amount)
