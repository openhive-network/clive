from __future__ import annotations

from typing import Final

from clive.__private.models.asset import Asset
from clive.__private.models.schemas import HiveDateTime, TransferOperation, convert_to_representation
from clive.__private.models.transaction import Transaction, TransactionLocalData

HEAD_BLOCK_TIME: Final[HiveDateTime] = HiveDateTime("2021-01-01T00:00:00")


def _create_transaction() -> Transaction:
    return Transaction(
        operations=[
            convert_to_representation(TransferOperation(from_="alice", to="bob", amount=Asset.hbd(1), memo="test"))
        ],
        ref_block_num=1,
        ref_block_prefix=2,
        expiration=HiveDateTime("2021-01-01T00:00:00"),
    )


def test_local_data_is_not_serialized() -> None:
    # ARRANGE
    transaction = _create_transaction()
    transaction.local.last_update_head_block_time = HEAD_BLOCK_TIME

    # ACT
    builtins = transaction.to_builtins()
    serialized = transaction.json()

    # ASSERT
    assert "local" not in builtins
    assert "_local" not in builtins
    assert "local" not in serialized


def test_local_data_is_set_in_transaction_built_from_builtins() -> None:
    # ARRANGE
    builtins = _create_transaction().to_builtins()

    # ACT
    transaction = Transaction.from_builtins(builtins)

    # ASSERT
    assert transaction.local == TransactionLocalData()
    assert transaction.to_builtins() == builtins


def test_copy_has_its_own_copy_of_local_data() -> None:
    # ARRANGE
    transaction = _create_transaction()
    transaction.local.last_update_head_block_time = HEAD_BLOCK_TIME

    # ACT
    copied = transaction.copy()
    copied.local.last_update_head_block_time = None

    # ASSERT
    assert transaction.local.last_update_head_block_time == HEAD_BLOCK_TIME
    assert copied == transaction
