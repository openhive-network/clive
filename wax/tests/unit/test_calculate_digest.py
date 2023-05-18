from __future__ import annotations

import pytest
from consts import ENCODING, MAINNET_CHAIN_ID, VALID_IDS_WITH_TRANSACTIONS

import wax


@pytest.mark.parametrize("trx_id", list(VALID_IDS_WITH_TRANSACTIONS.keys()))
def test_proper_digest(trx_id: str) -> None:
    result = wax.calculate_digest(VALID_IDS_WITH_TRANSACTIONS[trx_id].encode(ENCODING), MAINNET_CHAIN_ID)
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    assert result.result.decode(ENCODING) == trx_id
