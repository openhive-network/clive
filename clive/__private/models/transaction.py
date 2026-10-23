from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core.constants.date import TRANSACTION_EXPIRATION_TIMEDELTA_DEFAULT
from clive.__private.models.schemas import (
    AccountUpdate2Operation,
    AccountUpdateOperation,
    HiveDateTime,
    OperationRepresentationUnion,
    OperationUnion,
    TransactionId,
    Uint16t,
    Uint32t,
    convert_to_representation,
)
from clive.__private.models.schemas import Transaction as SchemasTransaction


@dataclass
class TransactionLocalData:
    """Runtime-only data attached to Transaction, excluded from serialization.

    Attributes:
        last_update_head_block_time: Head block time (from GDPO) captured when
            update_transaction_metadata was last called.
    """

    last_update_head_block_time: HiveDateTime | None = None


if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from clive.__private.core.accounts.accounts import KnownAccount
    from clive.__private.visitors.operation.operation_visitor import OperationVisitor


def _default_expiration() -> HiveDateTime:
    return HiveDateTime(HiveDateTime.now() + TRANSACTION_EXPIRATION_TIMEDELTA_DEFAULT)


@dataclass(kw_only=True)
class Transaction(SchemasTransaction):
    """
    Transaction of operations in the HF26 form.

    Runtime-only data (`local`) is kept in a slot, out of the fields - it is never serialized. Fields are annotated
    with builtins (models are built without validation), not with the validating field types of schemas.

    Attributes:
        operations: Operations in the HF26 form.
        ref_block_num: Number of the reference block (TaPoS).
        ref_block_prefix: Prefix of the reference block (TaPoS).
        expiration: Time of expiration.
        extensions: Extensions of the transaction.
        signatures: Signatures of the transaction.
    """

    __slots__ = ("_local",)

    operations: list[OperationRepresentationUnion] = field(default_factory=list)
    ref_block_num: Uint16t = 0
    ref_block_prefix: Uint32t = 0
    expiration: HiveDateTime = field(default_factory=_default_expiration)
    extensions: list[object] = field(default_factory=list)
    signatures: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._local = TransactionLocalData()

    def __bool__(self) -> bool:
        """Return True when there are any operations."""
        return bool(self.operations)

    def __contains__(self, operation: object) -> bool:
        if isinstance(operation, OperationUnion):
            return operation in self.operations_models
        return operation in self.operations

    def __iter__(self) -> Iterator[OperationUnion]:  # type: ignore[override]  # models iterate nothing, this one ops
        return iter(self.operations_models)

    def __len__(self) -> int:
        return len(self.operations)

    @property
    def local(self) -> TransactionLocalData:
        """Runtime-only data attached to the transaction, not serialized."""
        return self._local

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
    def convert_operations(cls, value: Iterable[OperationUnion]) -> list[OperationRepresentationUnion]:
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
        from clive.__private.core import iwax  # noqa: PLC0415

        return TransactionId(iwax.calculate_transaction_id(self))

    def reset(self) -> None:
        self.operations = []
        self.ref_block_num = Uint16t(0)
        self.ref_block_prefix = Uint32t(0)
        self.expiration = _default_expiration()
        self.extensions = []
        self.signatures = []
        self._local = TransactionLocalData()

    def swap_operations(self, index_1: int, index_2: int) -> None:
        self.operations[index_1], self.operations[index_2] = self.operations[index_2], self.operations[index_1]

    def unsign(self) -> None:
        self.signatures.clear()

    def with_hash(self) -> TransactionWithHash:
        return TransactionWithHash(
            operations=self.operations,
            ref_block_num=self.ref_block_num,
            ref_block_prefix=self.ref_block_prefix,
            expiration=self.expiration,
            extensions=self.extensions,
            signatures=self.signatures,
            transaction_id=self.calculate_transaction_id(),
        )

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
        from clive.__private.visitors.operation.potential_bad_account_collector import (  # noqa: PLC0415
            PotentialBadAccountCollector,
        )

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
        from clive.__private.visitors.operation.potential_known_account_collector import (  # noqa: PLC0415
            PotentialKnownAccountCollector,
        )

        visitor = PotentialKnownAccountCollector()
        self.accept(visitor)
        return visitor.get_unknown_accounts(already_known_accounts)

    def has_authority_update_operation(self, account_name: str) -> bool:
        """
        Check if the transaction contains any operation that modifies authority.

        Args:
            account_name: Name of the account to check for authority modification.

        Returns:
            True if any of operations are present in transaction, False otherwise.
        """
        return any(
            isinstance(operation, (AccountUpdate2Operation, AccountUpdateOperation))
            and operation.account == account_name
            for operation in self.operations_models
        )

    def remove_authority_update_operations(self, account_name: str) -> None:
        """
        Remove all operations that modify authority for the given account.

        Args:
            account_name: Name of the account whose authority modification operations should be removed.
        """
        for operation in self.operations_models:
            if (
                isinstance(operation, (AccountUpdate2Operation, AccountUpdateOperation))
                and operation.account == account_name
            ):
                self.remove_operation(operation)

    def _after_build(self) -> None:
        self.__post_init__()  # building by `from_builtins` does not call `__post_init__`


@dataclass(kw_only=True)
class TransactionWithHash(Transaction):
    transaction_id: str
