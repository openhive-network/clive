from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.iwax import validate_transaction
from clive.models import Asset, Transaction
from schemas.operations import TransferOperation

if TYPE_CHECKING:
    from clive.models import Operation


operations: Final[list[Operation]] = [TransferOperation(from_="alice", to="bob", amount=Asset.hive(10), memo="aaa")]


def test_valid_transaction() -> None:
    validate_transaction(Transaction(operations=operations))
