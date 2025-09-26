from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.transaction import Transaction
from clive_local_tools.helpers import get_transaction_id_from_output

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import Result


def get_transaction_id_from_result(result: Result) -> str:
    return get_transaction_id_from_output(result.stdout)


def load_transaction_from_file(transaction_path: Path) -> Transaction:
    return Transaction.parse_file(transaction_path)
