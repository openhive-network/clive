from __future__ import annotations

import re
from typing import TypeAlias, TypeVar

from clive.__private.core.decimal_conventer import DecimalConversionNotANumberError, DecimalConverter
from clive.exceptions import CliveError
from schemas.fields.assets import AssetHbdHF26, AssetHiveHF26, AssetVestsHF26

AssetAmountT = int | float | str

AssetT = TypeVar("AssetT", AssetHiveHF26, AssetHbdHF26, AssetVestsHF26)


class AssetError(CliveError):
    """Base class for all asset related errors."""


class AssetLegacyInvalidFormatError(CliveError):
    def __init__(self, value: str) -> None:
        super().__init__(f"Invalid asset format: {value}")


class AssetAmountInvalidFormatError(CliveError):
    def __init__(self, value: str) -> None:
        self.message = f"Invalid asset amount format: '{value}'. Should be a number."
        super().__init__(self.message)


class Asset:
    Hive: TypeAlias = AssetHiveHF26
    Hbd: TypeAlias = AssetHbdHF26
    Vests: TypeAlias = AssetVestsHF26
    LiquidT: TypeAlias = Hive | Hbd
    AnyT: TypeAlias = Hive | Hbd | Vests

    @classmethod
    def hive(cls, amount: AssetAmountT) -> Asset.Hive:
        """
        Create Hive asset.

        Args:
        ----
        amount: Amount of Hive.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return cls.__create(Asset.Hive, amount)

    @classmethod
    def hbd(cls, amount: AssetAmountT) -> Asset.Hbd:
        """
        Create Hbd asset.

        Args:
        ----
        amount: Amount of Hbd.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return cls.__create(Asset.Hbd, amount)

    @classmethod
    def vests(cls, amount: AssetAmountT) -> Asset.Vests:
        """
        Create Vests asset.

        Args:
        ----
        amount: Amount of Vests.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return cls.__create(Asset.Vests, amount)

    @classmethod
    def __create(cls, asset: type[AssetT], amount: AssetAmountT) -> AssetT:
        """
        Create asset.

        Args:
        ----
        asset: Asset type.
        amount: Amount of asset.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        try:
            amount = cls.__convert_amount_to_internal_representation(amount, asset)
        except DecimalConversionNotANumberError as error:
            raise AssetAmountInvalidFormatError(str(amount)) from error
        else:
            return asset(amount=amount)

    @classmethod
    def resolve_symbol(cls, symbol: str) -> type[Asset.AnyT]:
        match symbol.upper():
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
        return asset_cls(amount=cls.__convert_amount_to_internal_representation(amount, asset_cls))

    @classmethod
    def to_legacy(cls, asset: Asset.AnyT) -> str:
        return f"{cls.pretty_amount(asset)} {asset.get_asset_information().symbol[0]}"

    @classmethod
    def pretty_amount(cls, asset: Asset.AnyT) -> str:
        return f"{int(asset.amount) / 10**asset.precision :.{asset.precision}f}"

    @staticmethod
    def __convert_amount_to_internal_representation(amount: AssetAmountT, precision: int | type[Asset.AnyT]) -> int:
        """
        Convert given amount to internal representation of integer value.

        Raises
        ------
        DecimalConversionNotANumberError: If given amount is not a valid number.
        """
        precision = precision if isinstance(precision, int) else precision.get_asset_information().precision
        amount_decimal = DecimalConverter.convert(amount, precision=precision)
        return int(amount_decimal * 10**precision)
