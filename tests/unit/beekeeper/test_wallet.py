from __future__ import annotations

import json
from time import sleep
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.beekeeper.handle import ErrorResponseError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import BeekeeperLocal
    from clive.__private.core.beekeeper.model import ListWallets
    from tests import WalletInfo


def check_wallets(given: ListWallets, valid: list[str], *, unlocked: bool = True) -> None:
    assert len(given.wallets) == len(valid)
    for given_wallet in given.wallets:
        assert given_wallet.name in valid
        assert given_wallet.unlocked == unlocked


@pytest.mark.parametrize("wallet_name", ("test", "123"))
def test_create_wallet(beekeeper: BeekeeperLocal, wallet_name: str) -> None:
    # ARRANGE & ACT
    beekeeper.api.create(wallet_name=wallet_name)

    # ASSERT
    check_wallets(beekeeper.api.list_wallets(), [wallet_name])


@pytest.mark.parametrize("invalid_wallet_name", (",,,", "*", "   a   ", " ", "", json.dumps({"a": None, "b": 21.37})))
def test_invalid_wallet_names(beekeeper: BeekeeperLocal, invalid_wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(ErrorResponseError):
        beekeeper.api.create(wallet_name=invalid_wallet_name)


def test_wallet_open(beekeeper: BeekeeperLocal, wallet: WalletInfo) -> None:
    # ARRANGE
    beekeeper.restart()  # this will close

    # ACT & ASSERT
    check_wallets(beekeeper.api.list_wallets(), [])
    beekeeper.api.open(wallet_name=wallet.name)
    check_wallets(beekeeper.api.list_wallets(), [wallet.name], unlocked=False)


def test_wallet_unlock(beekeeper: BeekeeperLocal, wallet: WalletInfo) -> None:
    # ARRANGE
    beekeeper.api.lock_all()  # after creation wallet is opened and unlocked by default

    # ACT
    beekeeper.api.unlock(wallet_name=wallet.name, password=wallet.password)

    # ASSERT
    check_wallets(beekeeper.api.list_wallets(), [wallet.name])


@pytest.mark.random_fail
def test_timeout(beekeeper: BeekeeperLocal, wallet: WalletInfo) -> None:
    timeout: Final[int] = 5
    comparison_error_max_delta: Final[float] = 1.0

    # ARRANGE
    beekeeper.api.set_timeout(seconds=timeout)

    # ASSERT
    info = beekeeper.api.get_info()
    assert timeout - (info.timeout_time - info.now).total_seconds() <= comparison_error_max_delta
    check_wallets(beekeeper.api.list_wallets(), [wallet.name])

    # ACT
    sleep(timeout)

    # ASSERT
    check_wallets(beekeeper.api.list_wallets(), [wallet.name], unlocked=False)


def test_create_wallet_with_custom_password(beekeeper: BeekeeperLocal, wallet_name: str) -> None:
    # ARRANGE & ACT
    password = beekeeper.api.create(wallet_name=wallet_name, password=wallet_name).password

    # ASSERT
    assert password == wallet_name
