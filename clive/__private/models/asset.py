from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Generic, TypeAlias, TypeVar

from clive.__private.core.decimal_conventer import (
    DecimalConversionNotANumberError,
    DecimalConverter,
    DecimalConvertible,
)
from clive.exceptions import CliveError
from hiveio_api import Asset as PublicAsset
from schemas.fields.public import AssetKind, asset_info_of_nai, asset_info_of_symbol

if TYPE_CHECKING:
    from decimal import Decimal

AssetT = TypeVar("AssetT", bound=PublicAsset)

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


class UnknownAssetNaiError(AssetError):
    def __init__(self, nai: str) -> None:
        self.nai = nai
        message = f"Unknown asset nai: '{nai}'"
        super().__init__(message)


@dataclass(frozen=True)
class AssetFactoryHolder(Generic[AssetT]):  # noqa: UP046
    """
    Holds factory for asset.

    Attributes:
        asset_kind: Kind of the asset.
        asset_factory: Factory function to create an instance of the asset.
    """

    asset_kind: AssetKind
    asset_factory: AssetFactory[AssetT]


class Asset:
    """
    Factories and helpers of assets - all assets are instances of `hiveio_api.Asset`.

    The aliases name the kinds an asset of an annotation may have; they are the same class, so the kind of an asset is
    checked with `is_hive()`, `is_hbd()`, `is_vests()` and kinds are passed as `Asset.Kind` (`Asset.HIVE_KIND`, ...).

    Attributes:
        Hive: Asset of HIVE (annotations only).
        Hbd: Asset of HBD (annotations only).
        Vests: Asset of VESTS (annotations only).
        LiquidT: Asset of HIVE or HBD (annotations only).
        VotingT: Asset of HIVE or VESTS (annotations only).
        AnyT: Asset of any kind (annotations only).
        Kind: Kind of assets.
        HIVE_KIND: Kind of HIVE.
        HBD_KIND: Kind of HBD.
        VESTS_KIND: Kind of VESTS.
        LIQUID_TYPES: Kinds of liquid assets.
        VOTING_TYPES: Kinds of assets giving voting power.
    """

    Hive: TypeAlias = PublicAsset  # noqa: UP040  # annotations only - the kind is checked by `is_hive()`
    Hbd: TypeAlias = PublicAsset  # noqa: UP040  # annotations only - the kind is checked by `is_hbd()`
    Vests: TypeAlias = PublicAsset  # noqa: UP040  # annotations only - the kind is checked by `is_vests()`
    LiquidT: TypeAlias = PublicAsset  # noqa: UP040  # annotations only - HIVE or HBD
    VotingT: TypeAlias = PublicAsset  # noqa: UP040  # annotations only - HIVE or VESTS
    AnyT: TypeAlias = PublicAsset  # noqa: UP040  # annotations only
    Kind: TypeAlias = AssetKind  # noqa: UP040

    HIVE_KIND: Final[AssetKind] = PublicAsset.hive
    HBD_KIND: Final[AssetKind] = PublicAsset.hbd
    VESTS_KIND: Final[AssetKind] = PublicAsset.vests

    LIQUID_TYPES: Final[tuple[AssetKind, ...]] = (HIVE_KIND, HBD_KIND)
    VOTING_TYPES: Final[tuple[AssetKind, ...]] = (HIVE_KIND, VESTS_KIND)

    @classmethod
    def hive(cls, amount: AssetAmount) -> Asset.Hive:
        """
        Create Hive asset.

        Args:
            amount: Amount of Hive.

        Raises:
            AssetAmountInvalidFormatError: Raised when given amount is in invalid format.

        Returns:
            An instance of Hive asset with the specified amount.
        """
        return cls.__create(cls.HIVE_KIND, amount)

    @classmethod
    def hbd(cls, amount: AssetAmount) -> Asset.Hbd:
        """
        Create Hbd asset.

        Args:
            amount: Amount of Hbd.

        Raises:
            AssetAmountInvalidFormatError: Raised when given amount is in invalid format.

        Returns:
            An instance of Hbd asset with the specified amount.
        """
        return cls.__create(cls.HBD_KIND, amount)

    @classmethod
    def vests(cls, amount: AssetAmount) -> Asset.Vests:
        """
        Create Vests asset.

        Args:
            amount: Amount of Vests.

        Raises:
            AssetAmountInvalidFormatError: Raised when given amount is in invalid format.

        Returns:
            An instance of Vests asset with the specified amount.
        """
        return cls.__create(cls.VESTS_KIND, amount)

    @classmethod
    def ensure_liquid_type(cls, asset_type: Asset.Kind) -> Asset.Kind:
        assert asset_type in cls.LIQUID_TYPES, f"Asset is not liquid type, given type is {asset_type}"
        return asset_type

    @classmethod
    def ensure_voting_type(cls, asset_type: Asset.Kind) -> Asset.Kind:
        assert asset_type in cls.VOTING_TYPES, f"Asset is not voting type, given type is {asset_type}"
        return asset_type

    @classmethod
    def __create(cls, asset: Asset.Kind, amount: AssetAmount) -> Asset.AnyT:
        """
        Create asset.

        Args:
            asset: Asset type.
            amount: Amount of asset.

        Raises:
            AssetAmountInvalidFormatError: Raised when given amount is in invalid format.

        Returns:
            An instance of the specified asset type with the given amount.
        """
        try:
            amount = cls.__convert_amount_to_internal_representation(amount, asset)
        except DecimalConversionNotANumberError as error:
            raise AssetAmountInvalidFormatError(str(amount), "Should be a number.") from error
        else:
            return asset.satoshi(amount)

    @classmethod
    def resolve_symbol(cls, symbol: str) -> Asset.Kind:
        symbol = symbol.upper()
        asset_info = asset_info_of_symbol(symbol)
        if asset_info is None:
            raise UnknownAssetTypeError(symbol)
        return PublicAsset.kind_of(asset_info)

    @classmethod
    def resolve_nai(cls, nai: str) -> Asset.Kind:
        asset_info = asset_info_of_nai(nai)
        if asset_info is None:
            raise UnknownAssetNaiError(nai)
        return PublicAsset.kind_of(asset_info)

    @classmethod
    def from_legacy(cls, value: str) -> Asset.AnyT:
        from clive.__private.core.formatters.humanize import humanize_validation_result  # noqa: PLC0415
        from clive.__private.validators.asset_amount_validator import AssetAmountValidator  # noqa: PLC0415

        match = re.match(r"(\d+(?:\.\d+)?)\s*(\w+)", value)
        if not match:
            raise AssetLegacyInvalidFormatError(value)

        amount, symbol = match.groups()

        asset_kind = cls.resolve_symbol(symbol)

        result = AssetAmountValidator(asset_kind).validate(amount)
        if not result.is_valid:
            raise AssetAmountInvalidFormatError(amount, reason=humanize_validation_result(result))

        return asset_kind.satoshi(cls.__convert_amount_to_internal_representation(amount, asset_kind))

    @classmethod
    def to_legacy(cls, asset: Asset.AnyT) -> str:
        return f"{cls.pretty_amount(asset)} {cls.get_symbol(asset)}"

    @classmethod
    def pretty_amount(cls, asset: Asset.AnyT) -> str:
        return asset.pretty_amount()

    @classmethod
    def as_decimal(cls, asset: Asset.AnyT) -> Decimal:
        return asset.tokens

    @classmethod
    def __convert_amount_to_internal_representation(cls, amount: AssetAmount, precision: int | Asset.Kind) -> int:
        """
        Convert given amount to internal representation of integer value.

        Args:
            amount: Amount to convert.
            precision: Precision to determine how many decimal places to consider.

        Raises:
            DecimalConversionNotANumberError: If given amount is not a valid number.

        Returns:
            Internal representation of the amount.
        """
        precision = precision if isinstance(precision, int) else cls.get_precision(precision)
        amount_decimal = DecimalConverter.convert(amount, precision=precision)
        return int(amount_decimal * 10**precision)

    @staticmethod
    def get_symbol(asset: Asset.Kind | Asset.AnyT) -> str:
        return asset.info.get_symbol() if isinstance(asset, AssetKind) else asset.symbol

    @staticmethod
    def get_precision(asset: Asset.Kind | Asset.AnyT) -> int:
        return asset.info.precision if isinstance(asset, AssetKind) else asset.precision

    @staticmethod
    def get_nai(asset: Asset.Kind | Asset.AnyT) -> str:
        return asset.info.nai if isinstance(asset, AssetKind) else asset.nai

    @classmethod
    def get_kind(cls, asset: Asset.AnyT) -> Asset.Kind:
        """
        Get the kind of the asset - all assets are of the same class, they differ by their NAI.

        Args:
            asset: The asset to get the kind of.

        Returns:
            The kind of the asset, e.g. `Asset.HIVE_KIND`.
        """
        return cls.resolve_nai(asset.nai)

    @classmethod
    def is_hive(cls, asset: Asset.Kind | Asset.AnyT) -> bool:
        return cls.get_nai(asset) == cls.HIVE_KIND.info.nai

    @classmethod
    def is_hbd(cls, asset: Asset.Kind | Asset.AnyT) -> bool:
        return cls.get_nai(asset) == cls.HBD_KIND.info.nai

    @classmethod
    def is_vests(cls, asset: Asset.Kind | Asset.AnyT) -> bool:
        return cls.get_nai(asset) == cls.VESTS_KIND.info.nai
