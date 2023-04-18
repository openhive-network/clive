from __future__ import annotations

import json

import pytest

from clive.__private.core.beekeeper import Beekeeper


@pytest.mark.parametrize("wallet_name", ("test", "123", "test"))
def test_create_wallet(beekeeper: Beekeeper, wallet_name: str) -> None:
    # ARRANGE & ACT
    beekeeper.api.create(wallet_name=wallet_name)

    # ASSERT
    wallets = beekeeper.api.list_wallets().wallets
    assert len(wallets) == 1
    assert wallets[0].startswith(wallet_name)
    assert wallets[0].endswith("*")


@pytest.mark.parametrize("wallet_name", (",,,", "*", "   a   ", " ", "", json.dumps({"a": None, "b": 21.37})))
def test_invalid_wallet_names(beekeeper: Beekeeper, wallet_name: str) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(Beekeeper.ErrorResponseError):
        beekeeper.api.create(wallet_name=wallet_name)
