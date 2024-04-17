from __future__ import annotations

import re
from collections.abc import Callable
from typing import Generic, TypeAlias, TypeVar

from pydantic.generics import GenericModel

from clive.__private.core.decimal_conventer import (
    DecimalConversionNotANumberError,
    DecimalConverter,
    DecimalConvertible,
)
from clive.exceptions import CliveError
from clive.models.base import CliveBaseModel
from schemas.fields.assets import AssetHbdHF26, AssetHiveHF26, AssetVestsHF26

AssetT = TypeVar("AssetT", bound=AssetHiveHF26 | AssetHbdHF26 | AssetVestsHF26)
AssetExplicitT = TypeVar("AssetExplicitT", AssetHiveHF26, AssetHbdHF26, AssetVestsHF26)

AssetAmount = DecimalConvertible
AssetFactory = Callable[[AssetAmount], AssetT]


class AssetError(CliveError):
    """Base class for all asset related errors."""


class AssetLegacyInvalidFormatError(AssetError):
    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__(f"Invalid asset format: {value}")


class AssetAmountInvalidFormatError(AssetError):
    def __init__(self, value: str, reason: str = "") -> None:
        self.value = value
        message = f"Invalid asset amount format: '{value}'."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(message)


class UnknownAssetTypeError(AssetError):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        message = f"Unknown asset type: '{symbol}'."
        super().__init__(message)


class AssetFactoryHolder(CliveBaseModel, GenericModel, Generic[AssetT]):
    """Holds factory for asset."""

    class Config:
        frozen = True

    asset_cls: type[AssetT]
    asset_factory: AssetFactory[AssetT]


class Asset:
    Hive: TypeAlias = AssetHiveHF26
    Hbd: TypeAlias = AssetHbdHF26
    Vests: TypeAlias = AssetVestsHF26
    LiquidT: TypeAlias = Hive | Hbd
    VotingT: TypeAlias = Hive | Vests
    AnyT: TypeAlias = Hive | Hbd | Vests

    @classmethod
    def hive(cls, amount: AssetAmount) -> Asset.Hive:
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
    def hbd(cls, amount: AssetAmount) -> Asset.Hbd:
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
    def vests(cls, amount: AssetAmount) -> Asset.Vests:
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
    def __create(cls, asset: type[AssetExplicitT], amount: AssetAmount) -> AssetExplicitT:
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
            raise AssetAmountInvalidFormatError(str(amount), "Should be a number.") from error
        else:
            return asset(amount=amount)

    @classmethod
    def resolve_symbol(cls, symbol: str) -> type[Asset.AnyT]:
        symbol = symbol.upper()
        match symbol:
            case "HIVE" | "TESTS":
                return Asset.Hive
            case "HBD" | "TBD":
                return Asset.Hbd
            case "VESTS":
                return Asset.Vests
            case _:
                raise UnknownAssetTypeError(symbol)

    @classmethod
    def resolve_nai(cls, nai: str) -> type[Asset.AnyT]:
        if nai == cls.get_nai(cls.Hive):
            return Asset.Hive
        if nai == cls.get_nai(cls.Hbd):
            return Asset.Hbd
        if nai == cls.get_nai(cls.Vests):
            return Asset.Vests
        raise ValueError(f"Unknown asset nai: '{nai}'")

    @classmethod
    def from_legacy(cls, value: str) -> Asset.AnyT:
        from clive.__private.validators.asset_amount_validator import AssetAmountValidator

        match = re.match(r"(\d+(?:\.\d+)?)\s*(\w+)", value)
        if not match:
            raise AssetLegacyInvalidFormatError(value)

        amount, symbol = match.groups()

        asset_cls = cls.resolve_symbol(symbol)

        result = AssetAmountValidator(asset_cls).validate(amount)
        if not result.is_valid:
            reason = str(result.failure_descriptions)
            raise AssetAmountInvalidFormatError(amount, reason=reason)

        return asset_cls(amount=cls.__convert_amount_to_internal_representation(amount, asset_cls))

    @classmethod
    def to_legacy(cls, asset: Asset.AnyT) -> str:
        return f"{cls.pretty_amount(asset)} {cls.get_symbol(asset)}"

    @classmethod
    def pretty_amount(cls, asset: Asset.AnyT) -> str:
        return f"{int(asset.amount) / 10 ** asset.precision :.{asset.precision}f}"

    @classmethod
    def __convert_amount_to_internal_representation(cls, amount: AssetAmount, precision: int | type[Asset.AnyT]) -> int:
        """
        Convert given amount to internal representation of integer value.

        Raises
        ------
        DecimalConversionNotANumberError: If given amount is not a valid number.
        """
        precision = precision if isinstance(precision, int) else cls.get_precision(precision)
        amount_decimal = DecimalConverter.convert(amount, precision=precision)
        return int(amount_decimal * 10**precision)

    @staticmethod
    def get_symbol(asset: type[Asset.AnyT] | Asset.AnyT) -> str:
        return asset.get_asset_information().symbol[0]

    @staticmethod
    def get_precision(asset: type[Asset.AnyT] | Asset.AnyT) -> int:
        return asset.get_asset_information().precision

    @staticmethod
    def get_nai(asset: type[Asset.AnyT] | Asset.AnyT) -> str:
        return asset.get_asset_information().nai
