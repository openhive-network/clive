from __future__ import annotations

from typing import Final

import pytest

from clive.__private.core.keys.keys import (
    Key,
    PrivateKey,
    PrivateKeyAliased,
    PrivateKeyInvalidFormatError,
    PublicKey,
    PublicKeyAliased,
)

PRIVATE_KEY_RAW: Final[str] = "5KR3NuadE7foZtaCKxELf3gTtGeAuR82bPeSvf9BKDcT6B42GGw"
PRIVATE_KEY: Final[PrivateKey] = PrivateKey(value=PRIVATE_KEY_RAW)
PRIVATE_KEY_ALIAS: Final[PrivateKeyAliased] = PRIVATE_KEY.with_alias("my_key")

PUBLIC_KEY_RAW: Final[str] = PRIVATE_KEY.calculate_public_key().value
PUBLIC_KEY: Final[PublicKey] = PublicKey(value=PUBLIC_KEY_RAW)
PUBLIC_KEY_ALIAS: Final[PublicKeyAliased] = PUBLIC_KEY.with_alias("my_key")


@pytest.mark.parametrize(
    "first",
    [PUBLIC_KEY, PUBLIC_KEY_ALIAS, PRIVATE_KEY, PRIVATE_KEY_ALIAS],
    ids=["public_key", "public_key_alias", "private_key", "private_key_alias"],
)
@pytest.mark.parametrize(
    "second",
    [PUBLIC_KEY_RAW, PUBLIC_KEY, PUBLIC_KEY_ALIAS, PRIVATE_KEY_RAW, PRIVATE_KEY, PRIVATE_KEY_ALIAS],
    ids=["public_key_raw", "public_key", "public_key_alias", "private_key_raw", "private_key", "private_key_alias"],
)
def test_keys_equal_positive(first: Key, second: str | Key) -> None:
    # ACT & ASSERT
    assert first == second


@pytest.mark.parametrize(
    "first",
    [PUBLIC_KEY, PUBLIC_KEY_ALIAS, PRIVATE_KEY, PRIVATE_KEY_ALIAS],
    ids=["public_key", "public_key_alias", "private_key", "private_key_alias"],
)
@pytest.mark.parametrize(
    "second",
    [123, None, [], {}, "5K7WfKML9MDVBKGD7cPXNvHy8zM4bqsoTorqFiMecygbHdrcMhF"],
)
def test_keys_equal_negative(first: Key, second: str | Key) -> None:
    # ACT & ASSERT
    assert first != second


@pytest.mark.skip("Requires Key.determine_key_type to handle invalid keys")
@pytest.mark.parametrize("first", [PUBLIC_KEY, PUBLIC_KEY_ALIAS, PRIVATE_KEY, PRIVATE_KEY_ALIAS])
def test_comparing_with_not_a_key_string(first: Key) -> None:
    # ACT & ASSERT
    with pytest.raises(PrivateKeyInvalidFormatError):
        assert first != "not a key"


def test_different_alias_public_key() -> None:
    # ARRANGE
    public_key_alias_other = PUBLIC_KEY.with_alias("other_key")

    # ACT & ASSERT
    assert public_key_alias_other != PUBLIC_KEY_ALIAS
    assert public_key_alias_other != PRIVATE_KEY_ALIAS


def test_different_alias_private_key() -> None:
    # ARRANGE
    private_key_alias_other = PRIVATE_KEY.with_alias("other_key")

    # ACT & ASSERT
    assert private_key_alias_other != PUBLIC_KEY_ALIAS
    assert private_key_alias_other != PRIVATE_KEY_ALIAS


def test_comparing_public_key_to_other_public_key_raw() -> None:
    # ACT & ASSERT
    assert PrivateKey.generate().calculate_public_key().value != PUBLIC_KEY
