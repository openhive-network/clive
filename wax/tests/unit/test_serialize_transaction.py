from __future__ import annotations

import pytest
from consts import ENCODING, VALID_TRXS

import wax


@pytest.mark.parametrize("key", list(VALID_TRXS.keys()))
def test_serialize_transaction(key: str) -> None:
    result = wax.serialize_transaction(VALID_TRXS[key].encode(ENCODING))
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    assert result.result.decode(ENCODING) == key
