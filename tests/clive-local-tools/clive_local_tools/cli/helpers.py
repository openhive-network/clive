from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from click.testing import Result


def get_transaction_id_from_result(result: Result) -> str:
    stdout = result.stdout
    for line in stdout.split("\n"):
        transaction_id = line.partition('"transaction_id":')[2]
        if transaction_id:
            return transaction_id.strip(' "')
    pytest.fail(f"Could not find transaction id in stdout {stdout}")
