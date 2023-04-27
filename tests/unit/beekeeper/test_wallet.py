from __future__ import annotations

import json
from math import ceil
from time import sleep
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.beekeeper.handle import ErrorResponseError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.beekeeper.model import ListWallets
    from tests import WalletInfo


def check_wallets(given: ListWallets, valid: list[str], *, unlocked: bool = True) -> None:
    assert len(given.wallets) == len(valid)
    for given_wallet in given.wallets:
        assert given_wallet.name in valid
        assert given_wallet.unlocked == unlocked


@pytest.mark.parametrize("wallet_name", ("test", "123"))
def test_create_wallet(beekeeper: Beekeeper, wallet_name: str) -> None:
    # ARRANGE & ACT
    beekeeper.api.create(wallet_name=wallet_name)

    # ASSERT
    check_wallets(beekeeper.api.list_wallets(), [wallet_name])


@pytest.mark.parametrize("invalid_wallet_name", (",,,", "*", "   a   ", " ", "", json.dumps({"a": None, "b": 21.37})))
def test_invalid_wallet_names(beekeeper: Beekeeper, invalid_wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(ErrorResponseError):
        beekeeper.api.create(wallet_name=invalid_wallet_name)


def test_wallet_open(beekeeper: Beekeeper, wallet: WalletInfo) -> None:
    # ARRANGE
    beekeeper.restart()  # this will close

    # ACT & ASSERT
    check_wallets(beekeeper.api.list_wallets(), [])
    beekeeper.api.open(wallet_name=wallet.name)
    check_wallets(beekeeper.api.list_wallets(), [wallet.name], unlocked=False)


def test_wallet_unlock(beekeeper: Beekeeper, wallet: WalletInfo) -> None:
    # ARRANGE
    beekeeper.api.lock_all()  # after creation wallet is opened and unlocked by default

    # ACT
    beekeeper.api.unlock(wallet_name=wallet.name, password=wallet.password)

    # ASSERT
    check_wallets(beekeeper.api.list_wallets(), [wallet.name])


def test_timeout(beekeeper: Beekeeper, wallet: WalletInfo) -> None:
    timeout: Final[int] = 2
    amount_of_microseconds_in_second: Final[int] = 1_000_000

    # ARRANGE
    beekeeper.api.set_timeout(seconds=timeout)

    # ASSERT
    info = beekeeper.api.get_info()
    time_diff = info.timeout_time - info.now
    precise_amount_of_time = time_diff.seconds + (time_diff.microseconds / amount_of_microseconds_in_second)
    assert ceil(precise_amount_of_time) == timeout
    check_wallets(beekeeper.api.list_wallets(), [wallet.name])

    # ACT
    sleep(timeout)

    # ASSERT
    check_wallets(beekeeper.api.list_wallets(), [wallet.name], unlocked=False)


def test_create_wallet_with_custom_password(beekeeper: Beekeeper, wallet_name: str) -> None:
    # ARRANGE & ACT
    password = beekeeper.api.create(wallet_name=wallet_name, password=wallet_name).password

    # ASSERT
    assert password == wallet_name
