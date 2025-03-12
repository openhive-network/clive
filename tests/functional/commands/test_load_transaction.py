from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

import pytest

from clive.__private.core import iwax
from clive.__private.core.commands.load_transaction import LoadTransaction
from clive.__private.models import Asset, Transaction
from clive.__private.models.schemas import TransferOperation
from schemas.fields.hive_datetime import HiveDateTime
from schemas.fields.hive_int import HiveInt
from schemas.operations.representation_types import HF26RepresentationTransferOperation

if TYPE_CHECKING:
    from pathlib import Path

VALID_TRANSACTION: Final[Transaction] = Transaction(
    operations=[
        HF26RepresentationTransferOperation(
            value=TransferOperation(from_="alice", to="bob", amount=Asset.hbd(1), memo="test")
        )
    ],
    ref_block_num=HiveInt(1),
    ref_block_prefix=HiveInt(2),
    expiration=HiveDateTime("2021-01-01T00:00:00"),
    extensions=[],
    signatures=[],
)


@pytest.mark.parametrize("mode", ["json", "bin"])
async def test_loading_valid_transaction_file(tmp_path: Path, mode: Literal["json", "bin"]) -> None:
    # ARRANGE
    expected_transaction = VALID_TRANSACTION
    file_name = f"transaction.{mode}"
    file_path = tmp_path / file_name
    if mode == "json":
        file_path.write_text(expected_transaction.json())
    else:
        file_path.write_bytes(iwax.serialize_transaction(expected_transaction))

    # ACT
    result = await LoadTransaction(file_path=file_path).execute_with_result()

    # ASSERT
    assert result == expected_transaction
