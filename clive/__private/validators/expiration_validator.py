from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Final

from textual.validation import Function, ValidationResult, Validator

from clive.__private.core.constants.node import (
    TRANSACTION_EXPIRATION_TIMEDELTA_MAX,
    TRANSACTION_EXPIRATION_TIMEDELTA_MIN,
)
from clive.__private.core.shorthand_timedelta import (
    SHORTHAND_TIMEDELTA_EXAMPLE_SHORT,
    InvalidShorthandToTimedeltaError,
    shorthand_timedelta_to_timedelta,
    timedelta_to_shorthand_timedelta,
)
from clive.__private.models.schemas import HiveDateTime

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from datetime import datetime, timedelta


class ExpirationFormatParser(ABC):
    """Strategy for parsing and validating a specific expiration input format."""

    @property
    @abstractmethod
    def format_description(self) -> str: ...

    @abstractmethod
    def can_parse(self, value: str) -> bool: ...

    @abstractmethod
    def to_delta(self, value: str, head_block_time: datetime | None) -> timedelta | None: ...

    @abstractmethod
    def is_not_expired(self, value: str, head_block_time: datetime) -> bool: ...


class TimedeltaFormatParser(ExpirationFormatParser):
    def __init__(self, metadata_block_time: datetime | None = None) -> None:
        self._metadata_block_time = metadata_block_time

    @property
    def format_description(self) -> str:
        return f"relative (e.g. {SHORTHAND_TIMEDELTA_EXAMPLE_SHORT})"

    def can_parse(self, value: str) -> bool:
        try:
            shorthand_timedelta_to_timedelta(value)
        except InvalidShorthandToTimedeltaError:
            return False
        return True

    def to_delta(self, value: str, head_block_time: datetime | None) -> timedelta | None:  # noqa: ARG002
        if not self.can_parse(value):
            return None
        return shorthand_timedelta_to_timedelta(value)

    def is_not_expired(self, value: str, head_block_time: datetime) -> bool:
        delta = shorthand_timedelta_to_timedelta(value)
        ref = self._metadata_block_time if self._metadata_block_time is not None else head_block_time
        return (ref + delta) > head_block_time


class DatetimeFormatParser(ExpirationFormatParser):
    @property
    def format_description(self) -> str:
        return 'absolute (e.g. "2025-01-01T00:00:00")'

    def can_parse(self, value: str) -> bool:
        try:
            HiveDateTime(value)
        except ValueError:
            return False
        return True

    def to_delta(self, value: str, head_block_time: datetime | None) -> timedelta | None:
        if not self.can_parse(value) or head_block_time is None:
            return None
        abs_time = HiveDateTime(value)
        return abs_time - HiveDateTime(head_block_time)

    def is_not_expired(self, value: str, head_block_time: datetime) -> bool:
        abs_time = HiveDateTime(value)
        return abs_time > head_block_time


class ExpirationValidator(Validator):
    VALUE_TOO_SMALL_DESCRIPTION: Final[str] = (
        f"Value must be greater or equal {timedelta_to_shorthand_timedelta(TRANSACTION_EXPIRATION_TIMEDELTA_MIN)}."
        " Updating metadata recalculates expiration relative to head block time."
    )
    VALUE_TOO_LARGE_DESCRIPTION: Final[str] = (
        f"Value must be less or equal {timedelta_to_shorthand_timedelta(TRANSACTION_EXPIRATION_TIMEDELTA_MAX)}."
        " Updating metadata recalculates expiration relative to head block time."
    )
    EXPIRED_DESCRIPTION: Final[str] = "Transaction must not be expired."

    def __init__(
        self,
        parsers: Sequence[ExpirationFormatParser],
        head_block_time_provider: Callable[[], datetime | None] | None = None,
    ) -> None:
        super().__init__()
        self._parsers = parsers
        self._head_block_time_provider = head_block_time_provider

    @property
    def invalid_input_description(self) -> str:
        descriptions = " or ".join(p.format_description for p in self._parsers)
        return f"Incorrect format. Use {descriptions}."

    def _get_head_block_time(self) -> datetime | None:
        if self._head_block_time_provider is None:
            return None
        return self._head_block_time_provider()

    def validate(self, value: str) -> ValidationResult:
        validators = [
            Function(self._validate_format, self.invalid_input_description),
            Function(self._validate_not_expired, self.EXPIRED_DESCRIPTION),
            Function(self._validate_min_value, self.VALUE_TOO_SMALL_DESCRIPTION),
            Function(self._validate_max_value, self.VALUE_TOO_LARGE_DESCRIPTION),
        ]
        return ValidationResult.merge([validator.validate(value) for validator in validators])

    def _get_matching_parser(self, value: str) -> ExpirationFormatParser | None:
        return next((p for p in self._parsers if p.can_parse(value)), None)

    def _validate_format(self, value: str) -> bool:
        return self._get_matching_parser(value) is not None

    def _get_delta(self, value: str) -> timedelta | None:
        parser = self._get_matching_parser(value)
        if parser is None:
            return None
        return parser.to_delta(value, self._get_head_block_time())

    def _validate_not_expired(self, value: str) -> bool:
        head_block_time = self._get_head_block_time()
        if head_block_time is None:
            return True
        parser = self._get_matching_parser(value)
        if parser is None:
            return True
        return parser.is_not_expired(value, head_block_time)

    def _validate_min_value(self, value: str) -> bool:
        delta = self._get_delta(value)
        if delta is None:
            return True
        if delta.total_seconds() <= 0:
            return True  # handled by _validate_not_expired
        return delta >= TRANSACTION_EXPIRATION_TIMEDELTA_MIN

    def _validate_max_value(self, value: str) -> bool:
        delta = self._get_delta(value)
        if delta is None:
            return True
        return delta <= TRANSACTION_EXPIRATION_TIMEDELTA_MAX
