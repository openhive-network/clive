from __future__ import annotations

from typing import Final

import pytest

from clive.__private.core.keys import KeyManager, PrivateKey, PrivateKeyAliased, PublicKey, PublicKeyAliased

IMPORTED_PRIVATE_KEY_VALUE: Final[str] = "5JLRdaDKnc1fx3iy14Se89rLXuU42dLN81Z6KNSRAknwr2E1jYn"
IMPORTED_KEY_ALIAS: Final[str] = "my_key"

IMPORTED_PRIVATE_KEY: Final[PrivateKey] = PrivateKey(value=IMPORTED_PRIVATE_KEY_VALUE)
IMPORTED_PUBLIC_KEY: Final[PublicKey] = IMPORTED_PRIVATE_KEY.calculate_public_key()


async def _get_key_manager_with_imported_key() -> KeyManager:
    keys = KeyManager()
    keys.add_to_import(PrivateKeyAliased(value=IMPORTED_PRIVATE_KEY_VALUE, alias=IMPORTED_KEY_ALIAS))

    async def import_key(key: PrivateKeyAliased) -> PublicKeyAliased:
        return key.calculate_public_key()

    await keys.import_pending_to_beekeeper(import_key)

    assert len(keys) == 1, "Key manager should contain exactly one key."
    assert keys.first.value == IMPORTED_PUBLIC_KEY.value, "Key manager should contain the imported key."
    assert keys.first.alias == IMPORTED_KEY_ALIAS, "Key manager should contain the imported key."

    return keys


@pytest.mark.parametrize(
    "compare_key",
    [
        IMPORTED_PRIVATE_KEY_VALUE,
        IMPORTED_PUBLIC_KEY.value,
        IMPORTED_PRIVATE_KEY,
        IMPORTED_PUBLIC_KEY,
        IMPORTED_PRIVATE_KEY.with_alias(IMPORTED_KEY_ALIAS),
        IMPORTED_PUBLIC_KEY.with_alias(IMPORTED_KEY_ALIAS),
    ],
    ids=[
        "private_key_string",
        "public_key_string",
        "private_key_object",
        "public_key_object",
        "private_key_aliased_object",
        "public_key_aliased_object",
    ],
)
async def test_key_manager_contains(
    compare_key: str | PrivateKey | PublicKey | PrivateKeyAliased | PublicKeyAliased,
) -> None:
    # ARRANGE
    keys = await _get_key_manager_with_imported_key()

    # ACT & ASSERT
    assert compare_key in keys, f"Key manager should contain {compare_key}."


@pytest.mark.parametrize(
    "compare_key",
    [
        PrivateKey.generate().value,
        PrivateKey.generate().calculate_public_key().value,
        PrivateKey.generate(),
        PrivateKey.generate().calculate_public_key(),
        IMPORTED_PRIVATE_KEY.with_alias("different"),
        IMPORTED_PUBLIC_KEY.with_alias("different"),
        PrivateKey.generate(with_alias=IMPORTED_KEY_ALIAS),
        PrivateKey.generate(with_alias=IMPORTED_KEY_ALIAS).calculate_public_key(),
    ],
    ids=[
        "private_key_string",
        "public_key_string",
        "private_key_object",
        "public_key_object",
        "private_key_aliased_object_with_different_alias",
        "public_key_aliased_object_with_different_alias",
        "private_key_aliased_object_with_same_alias_different_value",
        "public_key_aliased_object_with_same_alias_different_value",
    ],
)
async def test_key_manager_does_not_contains(
    compare_key: str | PrivateKey | PublicKey | PrivateKeyAliased | PublicKeyAliased,
) -> None:
    # ARRANGE
    keys = await _get_key_manager_with_imported_key()

    # ACT & ASSERT
    assert compare_key not in keys, f"Key manager should not contain {compare_key}."
