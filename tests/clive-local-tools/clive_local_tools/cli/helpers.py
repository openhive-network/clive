from __future__ import annotations

import pytest
from click.testing import Result


def get_transaction_id_from_result(result: Result) -> str:
    stdout = result.stdout
    for line in stdout.split("\n"):
        transaction_id = line.partition('"transaction_id":')[2]
        if transaction_id:
            return transaction_id.strip(' "')
    pytest.fail(f"Could not find transaction id in stdout {stdout}")


def ensure_transaction_id(trx_id_or_result: Result | str) -> str:
    if isinstance(trx_id_or_result, Result):
        return get_transaction_id_from_result(trx_id_or_result)
    return trx_id_or_result
