from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.transaction import Transaction
from clive_local_tools.helpers import get_transaction_id_from_output

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.cli.result_wrapper import CLITestResult


def get_transaction_id_from_result(result: CLITestResult) -> str:
    return get_transaction_id_from_output(result.stdout)


def load_transaction_from_file(transaction_path: Path) -> Transaction:
    return Transaction.parse_file(transaction_path)
