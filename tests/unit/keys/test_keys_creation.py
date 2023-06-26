from __future__ import annotations

import pytest

from clive.__private.core.keys.keys import PrivateKey, PrivateKeyAliased, PrivateKeyInvalidFormatError


def test_creating_invalid_format_private_key() -> None:
    with pytest.raises(PrivateKeyInvalidFormatError):
        PrivateKey(value="invalid format")


def test_creating_invalid_format_private_key_aliased() -> None:
    with pytest.raises(PrivateKeyInvalidFormatError):
        PrivateKeyAliased(value="invalid format", alias="my_key")
