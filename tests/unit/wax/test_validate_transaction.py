from __future__ import annotations

import pytest

import wax

from .consts import ENCODING, VALID_SIG_DIGEST_WITH_TRANSACTIONS


@pytest.mark.parametrize(
    "sig_digest", list(VALID_SIG_DIGEST_WITH_TRANSACTIONS.keys()), ids=range(len(VALID_SIG_DIGEST_WITH_TRANSACTIONS))
)
def test_valid_transaction(sig_digest: str) -> None:
    result = wax.validate_transaction(VALID_SIG_DIGEST_WITH_TRANSACTIONS[sig_digest].encode(ENCODING))
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message.decode(ENCODING)
