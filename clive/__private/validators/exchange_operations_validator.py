from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Function, ValidationResult, Validator

from clive.__private.visitors.operation.potential_exchange_operations_account_collector import (
    PotentialExchangeOperationsAccountCollector,
)

if TYPE_CHECKING:
    from clive.__private.models import Transaction


class ExchangeOperationsValidator(Validator):
    """Validating operations in a transaction to exchange."""

    HBD_TRANSFER_MSG_ERROR: Final[str] = "The transfer to the exchange must be in HIVE, not HBD."
    MEMOLESS_HIVE_TRANSFER_MSG_ERROR: Final[str] = "The transfer to the exchange must include a memo."
    FORCE_REQUIRED_OPERATION_MSG_ERROR: str = (
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
    def is_invalid_transfer(cls, result: ValidationResult) -> bool:
        """Check if the transfer operation is invalid."""
        return (
            cls.HBD_TRANSFER_MSG_ERROR in result.failure_descriptions
            or cls.MEMOLESS_HIVE_TRANSFER_MSG_ERROR in result.failure_descriptions
        )

    @classmethod
    def is_force_required(cls, result: ValidationResult) -> bool:
        """Check if the force required validation is needed."""
        return cls.FORCE_REQUIRED_OPERATION_MSG_ERROR in result.failure_descriptions

    def validate(self, value: str) -> ValidationResult:
        """Validate the given value - exchange name."""
        validators = [
            Function(self._validate_hbd_transfer_operation, self.HBD_TRANSFER_MSG_ERROR),
            Function(self._validate_memoless_transfer_operation, self.MEMOLESS_HIVE_TRANSFER_MSG_ERROR),
        ]
        if not self._suppress_force_required_validation:
            validators.append(
                Function(
                    self._validate_force_required_operation,
                    self.FORCE_REQUIRED_OPERATION_MSG_ERROR,
                )
            )
        return ValidationResult.merge([validator.validate(value) for validator in validators])

    def _validate_hbd_transfer_operation(self, value: str) -> bool:
        """Validate if the transaction has a HBD transfer operations."""
        visitor = PotentialExchangeOperationsAccountCollector()
        self._transaction.accept(visitor)
        return not visitor.has_hbd_transfer_operations_to_account(value)

    def _validate_memoless_transfer_operation(self, value: str) -> bool:
        """Validate if the transaction has a memoless transfer operations."""
        visitor = PotentialExchangeOperationsAccountCollector()
        self._transaction.accept(visitor)
        return not visitor.has_memoless_transfer_operations_to_account(value)

    def _validate_force_required_operation(self, value: str) -> bool:
        """Validate if the transaction has a force required operations."""
        visitor = PotentialExchangeOperationsAccountCollector()
        self._transaction.accept(visitor)
        return not visitor.has_force_required_operations_to_account(value)


class ExchangeOperationsValidatorCli(ExchangeOperationsValidator):
    """CLI-specific validator for exchange operations."""

    FORCE_REQUIRED_OPERATION_MSG_ERROR: str = (
        f"{ExchangeOperationsValidator.FORCE_REQUIRED_OPERATION_MSG_ERROR}"
        "You can force the process by using the `--force` flag"
    )
