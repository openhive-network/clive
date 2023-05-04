from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import BeekeeperLocal
    from clive.__private.storage.mock_database import PrivateKeyAlias
    from tests import WalletInfo

PRIVATE_AND_PUBLIC_KEYS: Final[list[tuple[str, str]]] = [
    (
        "5HwHC7y2WtCL18J9QMqX7awDe1GDsUTg7cfw734m2qFkdMQK92q",
        "STM6jACfK3P5xYFJQvavCwz5M8KR5EW3TcmSesArj9LJVGAq85qor",
    ),
    (
        "5J7m49WCKnRBTo1HyJisBinn8Lk3syYaXsrzdFmfDxkejHLwZ1m",
        "STM5hjCkhcMKcXQMppa97XUbDR5dWC3c2K8h23P1ajEi2fT9YuagW",
    ),
    (
        "5JqStPwQgnXBdyRDDxCDyjfC8oNjgJuZsBkT6MMz6FopydAebbC",
        "STM5EjyFcCNidBSivAtTKvWWwWRNjakcRMB79QrbwMKprcTRBHtXz",
    ),
    (
        "5JowdvuiDxoeLhzoSEKK74TCiwTaUHvxtRH3fkbweVEJZEsQJoc",
        "STM8RgQ3yexUZjcVGxQ2i3cKywwKwhxqzwtCHPQznGUYvQ15ZvahW",
    ),
    (
        "5Khrc9PX4S8wAUUmX4h2JpBgf4bhvPyFT5RQ6tGfVpKEudwpYjZ",
        "STM77P1n96ojdXcKpd5BRUhVmk7qFTfM2q2UkWSKg63Xi7NKyK2Q1",
    ),
]


def assert_keys(given: list[str], valid: list[str]) -> None:
    assert sorted(valid) == sorted(given)


def test_key_create(beekeeper: BeekeeperLocal, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    pubkey = beekeeper.api.create_key(wallet_name=wallet.name).public_key

    # ASSERT
    assert_keys(beekeeper.api.get_public_keys().keys, [pubkey])


@pytest.mark.parametrize("prv_pub", PRIVATE_AND_PUBLIC_KEYS)
def test_key_import(beekeeper: BeekeeperLocal, prv_pub: tuple[str, str], wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    pub_key = beekeeper.api.import_key(wallet_name=wallet.name, wif_key=prv_pub[0]).public_key

    # ASSERT
    assert_keys([pub_key], [prv_pub[1]])
    assert_keys(beekeeper.api.get_public_keys().keys, [prv_pub[1]])


def test_import_multiple_keys(beekeeper: BeekeeperLocal, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    public_keys = []
    for prv, pub in PRIVATE_AND_PUBLIC_KEYS:
        beekeeper.api.import_key(wallet_name=wallet.name, wif_key=prv)
        public_keys.append(pub)

    # ASSERT
    assert_keys(beekeeper.api.get_public_keys().keys, public_keys)


def test_remove_key(beekeeper: BeekeeperLocal, wallet: WalletInfo, pubkey: PrivateKeyAlias) -> None:
    # ARRANGE, ACT & ASSERT
    assert_keys(beekeeper.api.get_public_keys().keys, [pubkey.key_name])
    beekeeper.api.remove_key(wallet_name=wallet.name, password=wallet.password, public_key=pubkey.key_name)
    assert_keys(beekeeper.api.get_public_keys().keys, [])
