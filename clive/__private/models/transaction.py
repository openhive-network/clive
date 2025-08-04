from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from clive.__private.models.schemas import (
    HiveDateTime,
    HiveInt,
    OperationRepresentationUnion,
    OperationUnion,
    Signature,
    TransactionId,
    convert_to_representation,
    field,
)
from clive.__private.models.schemas import Transaction as SchemasTransaction

if TYPE_CHECKING:
    from collections.abc import Iterator

    from clive.__private.core.accounts.accounts import KnownAccount
    from clive.__private.visitors.operation.operation_visitor import OperationVisitor


class Transaction(SchemasTransaction):
    operations: list[OperationRepresentationUnion] = field(default_factory=list)
    ref_block_num: HiveInt = field(default_factory=lambda: HiveInt(-1))
    ref_block_prefix: HiveInt = field(default_factory=lambda: HiveInt(-1))
    expiration: HiveDateTime = field(default_factory=lambda: HiveDateTime.now() + timedelta(minutes=30))
    extensions: list[Any] = field(default_factory=list)
    signatures: list[Signature] = field(default_factory=list)

    def __bool__(self) -> bool:
        """Return True when there are any operations."""
        return bool(self.operations)

    def __contains__(self, operation: OperationRepresentationUnion | OperationUnion) -> bool:  # type: ignore[override]
        if isinstance(operation, OperationUnion):
            return operation in self.operations_models
        return operation in self.operations

    def __iter__(self) -> Iterator[OperationUnion]:
        return iter(self.operations_models)

    def __len__(self) -> int:
        return len(self.operations)

    @property
    def is_signed(self) -> bool:
        return bool(self.signatures)

    @property
    def is_tapos_set(self) -> bool:
        return self.ref_block_num >= 0 and self.ref_block_prefix > 0

    @property
    def operations_models(self) -> list[OperationUnion]:
        """Get only the operation models from already stored operations representations."""
        return [op.value for op in self.operations]

    @classmethod
    def convert_operations(cls, value: Any) -> list[OperationRepresentationUnion]:  # noqa: ANN401
        assert isinstance(value, Iterable)
        return [convert_to_representation(op) for op in value]

    def add_operation(self, *operations: OperationUnion) -> None:
        operation_representations = self.convert_operations(operations)
        self.operations.extend(operation_representations)

    def remove_operation(self, *operations: OperationUnion) -> None:
        for op in self.operations:
            if op.value in operations:
                self.operations.remove(op)
                return

    def calculate_transaction_id(self) -> TransactionId:
        from clive.__private.core import iwax

        return TransactionId(iwax.calculate_transaction_id(self))

    def reset(self) -> None:
        self.operations = []
        self.ref_block_num = HiveInt(-1)
        self.ref_block_prefix = HiveInt(-1)
        self.expiration = HiveDateTime.now() + timedelta(minutes=30)
        self.extensions = []
        self.signatures = []

    def swap_operations(self, index_1: int, index_2: int) -> None:
        self.operations[index_1], self.operations[index_2] = self.operations[index_2], self.operations[index_1]

    def unsign(self) -> None:
        self.signatures.clear()

    def with_hash(self) -> TransactionWithHash:
        return TransactionWithHash(**self.dict(), transaction_id=self.calculate_transaction_id())

    def accept(self, visitor: OperationVisitor) -> None:
        """
        Accept a visitor and apply it to all operations in the transaction.

        Args:
            visitor: An instance that will process the operations.
        """
        for operation in self.operations_models:
            visitor.visit(operation)

    def get_bad_accounts(self, bad_accounts: Iterable[str]) -> list[str]:
        """
        Return all accounts names from transaction that are considered as bad account.

        Args:
            bad_accounts: Account names that are considered bad.

        Returns:
            Account names from the transaction that are present in the bad accounts collection.
        """
        from clive.__private.visitors.operation.potential_bad_account_collector import PotentialBadAccountCollector

        visitor = PotentialBadAccountCollector()
        self.accept(visitor)
        return visitor.get_bad_accounts(bad_accounts)

    def get_unknown_accounts(self, already_known_accounts: Iterable[KnownAccount]) -> list[str]:
        """
        Return all unknown accounts names from transaction.

        Args:
            already_known_accounts: Known accounts to exclude from the result.

        Returns:
            Account names from the transaction that are not present in the already known accounts collection.
        """
        from clive.__private.visitors.operation.potential_known_account_collector import PotentialKnownAccountCollector

        visitor = PotentialKnownAccountCollector()
        self.accept(visitor)
        return visitor.get_unknown_accounts(already_known_accounts)


class TransactionWithHash(Transaction, kw_only=True):
    transaction_id: TransactionId
