from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

import pytest

from clive.__private.core import iwax
from clive.__private.core.commands.load_transaction import LoadTransaction, LoadTransactionError
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import HiveDateTime, TransferOperation, convert_to_representation
from clive.__private.models.transaction import Transaction

if TYPE_CHECKING:
    from pathlib import Path

VALID_TRANSACTION: Final[Transaction] = Transaction(
    operations=[
        convert_to_representation(TransferOperation(from_="alice", to="bob", amount=Asset.hbd(1), memo="test"))
    ],
    ref_block_num=1,
    ref_block_prefix=2,
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


async def test_loading_transaction_file_with_missing_fields(tmp_path: Path) -> None:
    # ARRANGE
    file_path = tmp_path / "transaction.json"
    file_path.write_text('{"ref_block_num": 1}')

    # ACT
    result = await LoadTransaction(file_path=file_path).execute_with_result()

    # ASSERT
    assert result.ref_block_num == 1
    assert result.operations == []
    assert result.signatures == []


@pytest.mark.parametrize(
    "content",
    [
        "not a transaction",
        "[]",
        '"transaction"',
        '{"ref_block_num": "not a number"}',
        '{"operations": [{"type": "not_existing_operation", "value": {}}]}',
        '{"operations": [{"type": "transfer_operation", "value": {"from": "alice"}}]}',
        '{"not_a_field": 1}',
    ],
    ids=[
        "not_json",
        "json_array",
        "json_string",
        "invalid_field_value",
        "unknown_operation",
        "incomplete_operation",
        "unknown_field",
    ],
)
async def test_loading_invalid_transaction_file(tmp_path: Path, content: str) -> None:
    # ARRANGE
    file_path = tmp_path / "transaction.json"
    file_path.write_text(content)

    # ACT & ASSERT
    with pytest.raises(LoadTransactionError):
        await LoadTransaction(file_path=file_path).execute_with_result()
