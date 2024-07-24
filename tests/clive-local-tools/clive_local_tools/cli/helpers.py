from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.models.aliased import RecurrentTransferOperation

if TYPE_CHECKING:
    import test_tools as tt
    from click.testing import Result

from clive.__private.core.date_utils import timedelta_to_int_hours
from clive.__private.core.shorthand_timedelta import shorthand_timedelta_to_timedelta
from clive.models.aliased import (
    RecurrentTransferPairIdOperationExtension,
    RecurrentTransferPairIdRepresentation,
)


def get_transaction_id_from_result(result: Result) -> str:
    stdout = result.stdout
    for line in stdout.split("\n"):
        transaction_id = line.partition('"transaction_id":')[2]
        if transaction_id:
            return transaction_id.strip(' "')
    pytest.fail(f"Could not find transaction id in stdout {stdout}")


def get_prepared_recurrent_transfer_operation(  # noqa: PLR0913
    from_: str,
    to: str,
    amount: tt.Asset.HiveT | tt.Asset.HbdT,
    memo: str,
    pair_id: int,
    recurrence: str,
    executions: int,
) -> RecurrentTransferOperation:
    if pair_id != 0:
        recurrent_transfer_extension = RecurrentTransferPairIdOperationExtension(pair_id=pair_id)
        representation = RecurrentTransferPairIdRepresentation(
            type=recurrent_transfer_extension.get_name(), value=recurrent_transfer_extension
        )
        extensions = [representation.dict(by_alias=True)]
    else:
        extensions = []
    return RecurrentTransferOperation(
        from_=from_,
        to=to,
        amount=amount,
        memo=memo,
        recurrence=timedelta_to_int_hours(shorthand_timedelta_to_timedelta(recurrence)),
        executions=executions,
        extensions=extensions,
    )
