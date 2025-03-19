from __future__ import annotations

import pytest

from schemas.clive.validate_schema_field import validate_schema_field
from clive.__private.models.schemas import TransactionId


def get_transaction_id_from_output(output: str) -> str:
    for line in output.split("\n"):
        transaction_id = line.partition('"transaction_id":')[2]
        if transaction_id:
            transaction_id_field = transaction_id.strip(' "')
            validate_schema_field(TransactionId, transaction_id_field)
            return transaction_id_field
    pytest.fail(f"Could not find transaction id in output {output}")
