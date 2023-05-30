from __future__ import annotations

import pytest

import wax

from .consts import ENCODING, VALID_IDS_WITH_TRANSACTIONS


@pytest.mark.parametrize(
    "trx_id", list(VALID_IDS_WITH_TRANSACTIONS.keys()), ids=range(len(VALID_IDS_WITH_TRANSACTIONS))
)
def test_valid_transaction(trx_id: str) -> None:
    result = wax.validate_transaction(VALID_IDS_WITH_TRANSACTIONS[trx_id].encode(ENCODING))
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message.decode(ENCODING)
