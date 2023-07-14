from __future__ import annotations

import pytest

import wax

from .consts import ENCODING, MAINNET_CHAIN_ID, VALID_SIG_DIGEST_WITH_TRANSACTIONS


@pytest.mark.parametrize("trx_id", list(VALID_SIG_DIGEST_WITH_TRANSACTIONS.keys()))
def test_proper_sig_digest(trx_id: str) -> None:
    result = wax.calculate_sig_digest(VALID_SIG_DIGEST_WITH_TRANSACTIONS[trx_id].encode(ENCODING), MAINNET_CHAIN_ID)
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    assert result.result.decode(ENCODING) == trx_id
