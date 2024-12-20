from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.helpers import get_transaction_id_from_output

if TYPE_CHECKING:
    from click.testing import Result


def get_transaction_id_from_result(result: Result) -> str:
    return get_transaction_id_from_output(result.stdout)
