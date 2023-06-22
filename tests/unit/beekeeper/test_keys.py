from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.keys.keys import PrivateKey, PublicKey
    from tests import WalletInfo

PRIVATE_AND_PUBLIC_KEYS: Final[list[tuple[str, str]]] = [
    (
        "5HwHC7y2WtCL18J9QMqX7awDe1GDsUTg7cfw734m2qFkdMQK92q",
        "6jACfK3P5xYFJQvavCwz5M8KR5EW3TcmSesArj9LJVGAq85qor",
    ),
    (
        "5J7m49WCKnRBTo1HyJisBinn8Lk3syYaXsrzdFmfDxkejHLwZ1m",
        "5hjCkhcMKcXQMppa97XUbDR5dWC3c2K8h23P1ajEi2fT9YuagW",
    ),
    (
        "5JqStPwQgnXBdyRDDxCDyjfC8oNjgJuZsBkT6MMz6FopydAebbC",
        "5EjyFcCNidBSivAtTKvWWwWRNjakcRMB79QrbwMKprcTRBHtXz",
    ),
    (
        "5JowdvuiDxoeLhzoSEKK74TCiwTaUHvxtRH3fkbweVEJZEsQJoc",
        "8RgQ3yexUZjcVGxQ2i3cKywwKwhxqzwtCHPQznGUYvQ15ZvahW",
    ),
    (
        "5Khrc9PX4S8wAUUmX4h2JpBgf4bhvPyFT5RQ6tGfVpKEudwpYjZ",
        "77P1n96ojdXcKpd5BRUhVmk7qFTfM2q2UkWSKg63Xi7NKyK2Q1",
    ),
]


def assert_keys(given: list[str], valid: list[str]) -> None:
    def normalize(keys: list[str]) -> list[str]:
        return [(key[3:] if key.startswith(("TST", "STM")) else key) for key in keys]

    assert sorted(normalize(valid)) == sorted(normalize(given))


@pytest.mark.parametrize("prv_pub", PRIVATE_AND_PUBLIC_KEYS)
def test_key_import(beekeeper: Beekeeper, prv_pub: tuple[str, str], wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    pub_key = beekeeper.api.import_key(wallet_name=wallet.name, wif_key=prv_pub[0]).public_key

    # ASSERT
    assert_keys([pub_key], [prv_pub[1]])
    assert_keys(beekeeper.api.get_public_keys().keys, [prv_pub[1]])


def test_import_multiple_keys(beekeeper: Beekeeper, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    public_keys = []
    for prv, pub in PRIVATE_AND_PUBLIC_KEYS:
        beekeeper.api.import_key(wallet_name=wallet.name, wif_key=prv)
        public_keys.append(pub)

    # ASSERT
    assert_keys(beekeeper.api.get_public_keys().keys, public_keys)


def test_remove_key(beekeeper: Beekeeper, wallet: WalletInfo, key_pair: tuple[PublicKey, PrivateKey]) -> None:
    # ARRANGE
    public_key, private_key = key_pair
    beekeeper.api.import_key(wallet_name=wallet.name, wif_key=private_key.value)

    # ACT & ASSERT
    assert_keys(beekeeper.api.get_public_keys().keys, [public_key.value])
    beekeeper.api.remove_key(wallet_name=wallet.name, password=wallet.password, public_key=public_key.value)
    assert_keys(beekeeper.api.get_public_keys().keys, [])
