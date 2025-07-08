from __future__ import annotations

import decimal
import warnings
from decimal import Decimal

from clive.exceptions import CliveError


class DecimalConversionError(CliveError):
    """Raised when decimal conversion fails."""


class DecimalConversionNotANumberError(CliveError):
    """Raised when decimal conversion fails because the value is not a number."""


DecimalConvertible = int | str | Decimal


class DecimalConverter:
    @classmethod
    def get_precision(cls, amount: DecimalConvertible) -> int:
        """
        Get precision of given amount.

        Args:
            amount: Amount to get precision of.

        Returns:
            Precision of the amount.
        """
        converted = cls.convert(amount)
        exponent = int(converted.as_tuple().exponent)
        return -1 * exponent

    @classmethod
    def convert(cls, amount: DecimalConvertible, *, precision: int | None = None) -> Decimal:
        """
        Convert given amount to Decimal.

        Args:
            amount: Amount to convert.
            precision: Precision of the amount.

        Raises:
            DecimalConversionNotANumberError: Raised when given amount is in invalid format.

        Returns:
            Converted amount.
        """
        try:
            converted = Decimal(amount)
        except decimal.InvalidOperation as error:
            raise DecimalConversionNotANumberError(f"Given {amount=} is not a number.") from error

        if precision is not None:
            cls.__assert_precision_is_positive(precision)
            cls.__warn_if_precision_might_be_lost(converted, precision)
            converted = cls.round_to_precision(converted, precision)

        return converted

    @staticmethod
    def __assert_precision_is_positive(precision: int) -> None:
        if precision < 0:
            raise ValueError("Precision must be a positive integer.")

    @staticmethod
    def round_to_precision(amount: Decimal, precision: int) -> Decimal:
        exponent = Decimal(10) ** (-1 * precision)
        return amount.quantize(exponent)

    @classmethod
    def __warn_if_precision_might_be_lost(cls, amount: Decimal, precision: int) -> None:
        rounded_amount = cls.round_to_precision(amount, precision)
        if rounded_amount != amount:
            warnings.warn(
                (
                    "Precision lost during value creation.\n"
                    "\n"
                    f"Value of {amount} was requested, but it was rounded to {rounded_amount},\n"
                    f"because precision of this value is {precision} ({pow(0.1, precision):.{precision}f})."
                ),
                stacklevel=1,
            )
