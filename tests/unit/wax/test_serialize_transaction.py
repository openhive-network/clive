from __future__ import annotations

import json
from typing import Any, Final

import pytest

import wax

from .consts import ENCODING, VALID_TRXS

TRX_BINARY_ALL_DEFAULTS: Final[bytes] = b"00000000000000000000000000"

TRX_DICT_WITH_ALL_DEFAULTS: Final[dict[str, Any]] = {
    "ref_block_num": 0,
    "ref_block_prefix": 0,
    "expiration": "1970-01-01T00:00:00",
    "extensions": [],
    "signatures": [],
    "operations": [],
}


@pytest.mark.parametrize("trx_binary", list(VALID_TRXS), ids=range(len(VALID_TRXS)))
def test_serialize_transaction(trx_binary: bytes) -> None:
    # ARRANGE
    encoded_transaction_json = json.dumps(VALID_TRXS[trx_binary]).encode(ENCODING)
    expected_trx_binary = trx_binary

    # ACT
    result = wax.serialize_transaction(encoded_transaction_json)

    # ASSERT
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    assert result.result == expected_trx_binary


@pytest.mark.parametrize("trx_json", [{}, TRX_DICT_WITH_ALL_DEFAULTS], ids=["empty dict", "dict with all defaults"])
def test_serialize_empty_transaction(trx_json: dict[str, Any]) -> None:
    # ARRANGE
    encoded_transaction_json = json.dumps(trx_json).encode(ENCODING)
    expected_trx_binary = TRX_BINARY_ALL_DEFAULTS

    # ACT
    result = wax.serialize_transaction(encoded_transaction_json)

    # ASSERT
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    assert result.result == expected_trx_binary


@pytest.mark.parametrize("trx_binary", list(VALID_TRXS), ids=range(len(VALID_TRXS)))
def test_deserialize_transaction(trx_binary: bytes) -> None:
    # ARRANGE
    expected_transaction = VALID_TRXS[trx_binary]

    # ACT
    result = wax.deserialize_transaction(trx_binary)

    # ASSERT
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    decoded_transaction = json.loads(result.result.decode(ENCODING))
    assert decoded_transaction == expected_transaction


def test_deserialize_empty_transaction() -> None:
    # ARRANGE
    trx_binary = TRX_BINARY_ALL_DEFAULTS
    expected_transaction = TRX_DICT_WITH_ALL_DEFAULTS

    # ACT
    result = wax.deserialize_transaction(trx_binary)

    # ASSERT
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    decoded_transaction = json.loads(result.result.decode(ENCODING))
    assert decoded_transaction == expected_transaction
