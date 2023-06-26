from __future__ import annotations

from clive.__private.core.keys import KeyManager, PrivateKeyAliased


def test_key_manager_contains() -> None:
    # ARRANGE
    keys = KeyManager()

    private_key = PrivateKeyAliased.create(with_alias="my_key")
    keys.add(private_key.calculate_public_key())

    # ACT & ASSERT
    assert private_key in keys
