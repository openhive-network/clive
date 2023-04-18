from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper
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


def test_key_create(beekeeper: Beekeeper, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    pubkey = beekeeper.api.create_key(wallet_name=wallet.name).public_key

    # ASSERT
    keys = beekeeper.api.get_public_keys().keys
    assert len(keys) == 1
    assert keys[0] == pubkey


@pytest.mark.parametrize("prv_pub", PRIVATE_AND_PUBLIC_KEYS)
def test_key_import(beekeeper: Beekeeper, prv_pub: tuple[str, str], wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    beekeeper.api.import_key(wallet_name=wallet.name, wif_key=prv_pub[0])

    # ASSERT
    keys = beekeeper.api.get_public_keys().keys
    assert len(keys) == 1
    assert keys[0] == prv_pub[1]


def test_import_multiple_keys(beekeeper: Beekeeper, wallet: WalletInfo) -> None:
    # ARRANGE & ACT
    public_keys = set()
    for prv, pub in PRIVATE_AND_PUBLIC_KEYS:
        beekeeper.api.import_key(wallet_name=wallet.name, wif_key=prv)
        public_keys.add(pub)

    # ASSERT
    keys = beekeeper.api.get_public_keys().keys
    assert len(public_keys) == len(keys)
    for key in keys:
        assert key in public_keys
