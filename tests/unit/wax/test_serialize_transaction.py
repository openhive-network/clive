from __future__ import annotations

import json

import pytest

import wax

from .consts import ENCODING, VALID_TRXS


@pytest.mark.parametrize("trx_binary", list(VALID_TRXS), ids=range(len(VALID_TRXS)))
def test_serialize_transaction(trx_binary: bytes) -> None:
    # ARRANGE
    encoded_transaction_json = json.dumps(VALID_TRXS[trx_binary]).encode(ENCODING)

    # ACT
    result = wax.serialize_transaction(encoded_transaction_json)

    # ASSERT
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    assert result.result == trx_binary
