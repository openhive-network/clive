from __future__ import annotations

import json
from typing import Final

import pytest

from clive.__private.core.beekeeper import Beekeeper


@pytest.mark.parametrize("wallet_name", ("test", "123", "test"))
def test_create_wallet(beekeeper: Beekeeper, wallet_name: str) -> None:
    # ARRANGE & ACT
    beekeeper.api.create(wallet_name=wallet_name)

    # ASSERT
    wallets = beekeeper.api.list_wallets().wallets
    assert len(wallets) == 1
    assert wallets[0].name == wallet_name
    assert wallets[0].unlocked


@pytest.mark.parametrize("wallet_name", (",,,", "*", "   a   ", " ", "", json.dumps({"a": None, "b": 21.37})))
def test_invalid_wallet_names(beekeeper: Beekeeper, wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(Beekeeper.ErrorResponseError):
        beekeeper.api.create(wallet_name=wallet_name)


def test_wallet_open(beekeeper: Beekeeper) -> None:
    wallet_name: Final[str] = "test"

    # ARRANGE
    beekeeper.api.create(wallet_name=wallet_name)
    beekeeper.restart()  # this will close

    # ACT & ASSERT
    assert not beekeeper.api.list_wallets().wallets
    beekeeper.api.open(wallet_name=wallet_name)
    wallets = beekeeper.api.list_wallets().wallets
    assert len(wallets) == 1
    assert wallets[0].name == wallet_name
    assert not wallets[0].unlocked


def test_wallet_unlock(beekeeper: Beekeeper) -> None:
    wallet_name: Final[str] = "test"

    # ARRANGE
    password = beekeeper.api.create(wallet_name=wallet_name).password
    beekeeper.api.lock_all()  # after creation wallet is opened and unlocked by default

    # ACT
    beekeeper.api.unlock(wallet_name=wallet_name, password=password)

    # ASSERT
    wallets = beekeeper.api.list_wallets().wallets
    assert len(wallets) == 1
    assert wallets[0].name == wallet_name
    assert wallets[0].unlocked
