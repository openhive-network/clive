from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.iwax import validate_transaction
from clive.models.asset import Asset
from clive.models.transaction import Transaction
from clive.models.transfer_operation import TransferOperation

if TYPE_CHECKING:
    from clive.models.operation import Operation


operations: Final[list[Operation]] = [TransferOperation(from_="alice", to="bob", amount=Asset.hive(10), memo="aaa")]


def test_valid_transaction() -> None:
    validate_transaction(Transaction(operations=operations))
