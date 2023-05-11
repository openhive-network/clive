from __future__ import annotations

import re
from typing import Literal

from schemas.__private.hive_fields_schemas import AssetHbdNai, AssetHiveNai, AssetVestsNai

AssetT = AssetHiveNai | AssetHbdNai | AssetVestsNai


class Asset:
    @classmethod
    def hive(cls, amount: float) -> AssetHiveNai:
        return AssetHiveNai(amount=cls.float_to_nai_int(amount, AssetHiveNai))

    @classmethod
    def hbd(cls, amount: float) -> AssetHbdNai:
        return AssetHbdNai(amount=cls.float_to_nai_int(amount, AssetHbdNai))

    @classmethod
    def vests(cls, amount: float) -> AssetVestsNai:
        return AssetVestsNai(amount=cls.float_to_nai_int(amount, AssetVestsNai))

    @classmethod
    def float_to_nai_int(cls, number: float, asset_type: type[AssetT]) -> int:
        result = number * (10 ** asset_type.get_precision())
        assert result == int(result), "invalid precision"
        return int(result)

    @classmethod
    def resolve_symbol(cls, symbol: Literal["HIVE", "TESTS", "HBD", "TBD", "VESTS"] | str) -> type[AssetT]:
        match symbol:
            case ["HIVE", "TESTS"]:
                return AssetHiveNai
            case ["HBD", "TBD"]:
                return AssetHbdNai
            case "VESTS":
                return AssetVestsNai
        raise ValueError(f"Unknown asset type: '{symbol}'")

    @classmethod
    def from_legacy(cls, legacy: str) -> AssetT:
        legacy_parsing_regex = re.compile(r"([0-9]+\.[0-9]+) ([A-Z]+)")
        parsed = legacy_parsing_regex.match(legacy)
        assert parsed is not None
        amount = int(parsed.group(1).replace(".", ""))
        symbol = parsed.group(2)
        return cls.resolve_symbol(symbol)(amount=amount)
