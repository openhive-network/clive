from __future__ import annotations

import pytest

from clive.__private.models.schemas import TransactionId
from schemas.decoders import is_matching_model


def get_transaction_id_from_output(output: str) -> str:
    for line in output.split("\n"):
        transaction_id = line.partition('"transaction_id":')[2]
        if transaction_id:
            transaction_id_field = transaction_id.strip(' "')
            is_matching_model(transaction_id_field, TransactionId)
            return transaction_id_field
    pytest.fail(f"Could not find transaction id in output {output}")
