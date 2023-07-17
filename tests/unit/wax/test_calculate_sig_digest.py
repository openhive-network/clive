from __future__ import annotations

import pytest

import wax

from .consts import ENCODING, MAINNET_CHAIN_ID, VALID_SIG_DIGEST_WITH_TRANSACTIONS


@pytest.mark.parametrize("sig_digest", list(VALID_SIG_DIGEST_WITH_TRANSACTIONS))
def test_proper_sig_digest(sig_digest: str) -> None:
    result = wax.calculate_sig_digest(VALID_SIG_DIGEST_WITH_TRANSACTIONS[sig_digest].encode(ENCODING), MAINNET_CHAIN_ID)
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message
    assert result.result.decode(ENCODING) == sig_digest
