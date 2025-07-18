from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Function, ValidationResult, Validator

from clive.__private.visitors.operation.potential_exchange_operations_account_collector import (
    PotentialExchangeOperationsAccountCollector,
)

if TYPE_CHECKING:
    from typing import ClassVar

    from clive.__private.models import Transaction


class ExchangeOperationsValidator(Validator):
    """
    Validating operations in a transaction to exchange.

    Attributes:
        HBD_TRANSFER_MSG_ERROR: Error message for HBD transfer operations.
        MEMOLESS_HIVE_TRANSFER_MSG_ERROR: Error message for memoless Hive transfer operations.
        UNSAFE_EXCHANGE_OPERATION_MSG_ERROR: Error message for unsafe exchange operations.

    Args:
        transaction: The transaction to validate.
        suppress_force_validation: If True, suppresses validation of unsafe exchange operations.
    """

    HBD_TRANSFER_MSG_ERROR: Final[str] = "The transfer to the exchange must be in HIVE, not HBD."
    MEMOLESS_HIVE_TRANSFER_MSG_ERROR: Final[str] = (
        "The transfer to the exchange must include a memo. Please check the memo of your exchange account."
    )

    UNSAFE_EXCHANGE_OPERATION_MSG_ERROR: ClassVar[str] = (
        "Exchanges usually support only the transfer operation, while other operation to a known exchange was detected."
    )

    def __init__(
        self,
        transaction: Transaction,
        *,
        suppress_force_validation: bool = False,
    ) -> None:
        super().__init__()
        self._suppress_force_required_validation = suppress_force_validation
        self._transaction = transaction

    @classmethod
    def has_unsafe_transfer_to_exchange(cls, result: ValidationResult) -> bool:
        """
        Check if unsafe exchange transfer was detected in the result .

        Args:
            result: The validation result to check.

        Returns:
            True if unsafe transfer to exchange was detected, False otherwise.
        """
        return (
            cls.HBD_TRANSFER_MSG_ERROR in result.failure_descriptions
            or cls.MEMOLESS_HIVE_TRANSFER_MSG_ERROR in result.failure_descriptions
        )

    @classmethod
    def has_unsafe_operation_to_exchange(cls, result: ValidationResult) -> bool:
        """Check if unsafe exchange operations was detected in the result ."""
        return cls.UNSAFE_EXCHANGE_OPERATION_MSG_ERROR in result.failure_descriptions

    def validate(self, value: str) -> ValidationResult:
        """Validate the given value - exchange name."""
        validators = [
            Function(self._validate_hbd_transfer_operation, self.HBD_TRANSFER_MSG_ERROR),
            Function(self._validate_memoless_transfer_operation, self.MEMOLESS_HIVE_TRANSFER_MSG_ERROR),
        ]
        if not self._suppress_force_required_validation:
            validators.append(
                Function(
                    self._validate_unsafe_exchange_operation,
                    self.UNSAFE_EXCHANGE_OPERATION_MSG_ERROR,
                )
            )
        return ValidationResult.merge([validator.validate(value) for validator in validators])

    def _validate_hbd_transfer_operation(self, value: str) -> bool:
        """Validate if the transaction has a HBD transfer operations."""
        visitor = PotentialExchangeOperationsAccountCollector()
        self._transaction.accept(visitor)
        return not visitor.has_hbd_transfer_operations_to_exchange(value)

    def _validate_memoless_transfer_operation(self, value: str) -> bool:
        """Validate if the transaction has a memoless transfer operations."""
        visitor = PotentialExchangeOperationsAccountCollector()
        self._transaction.accept(visitor)
        return not visitor.has_memoless_transfer_operations_to_exchange(value)

    def _validate_unsafe_exchange_operation(self, value: str) -> bool:
        """Validate if the transaction has unsafe exchange operations."""
        visitor = PotentialExchangeOperationsAccountCollector()
        self._transaction.accept(visitor)
        return not visitor.has_unsafe_operation_to_exchange(value)


class ExchangeOperationsValidatorCli(ExchangeOperationsValidator):
    """CLI-specific validator for exchange operations."""

    UNSAFE_EXCHANGE_OPERATION_MSG_ERROR: ClassVar[str] = (
        f"{ExchangeOperationsValidator.UNSAFE_EXCHANGE_OPERATION_MSG_ERROR}"
        " You can force the process by using the `--force` flag."
    )
