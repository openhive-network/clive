from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from click.testing import Result


def get_transaction_id_from_result(result: Result) -> str | None:
    stdout = result.stdout
    for line in stdout.split("\n"):
        transaction_id = line.partition('"transaction_id":')[2]
        if transaction_id:
            return transaction_id.strip(' "')
    return None
