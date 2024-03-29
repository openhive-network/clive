from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.exceptions import CommunicationError
from clive_local_tools.data.models import WalletInfo

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper

SPECIAL_CASES: Final[list[str]] = [".", "_", "-", "@"]
ALLOWED_CHARS: Final[list[str]] = [chr(i) for i in range(32, 126) if chr(i).isalnum() or chr(i) in SPECIAL_CASES]
NOT_ALLOWED_CHARS: Final[list[str]] = [chr(i) for i in range(32, 126) if chr(i) not in ALLOWED_CHARS]


async def test_api_create(beekeeper: Beekeeper) -> None:
    """Test test_api_create will test beekeeper_api.create api call."""
    # ARRANGE
    wallet = WalletInfo(password="password", name="test_api_create_wallet")
    wallets = (await beekeeper.api.list_wallets()).wallets
    assert len(wallets) == 0, "At the beginning there should be no wallets."

    # ACT
    await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)
    wallets = (await beekeeper.api.list_wallets()).wallets

    # ASSERT
    assert len(wallets) == 1, "There should be only one wallet."
    assert wallets[0].name == wallet.name, "Wallet names should match."
    assert wallets[0].unlocked, "Wallet should be unlocked after creation."


async def test_api_create_double_same_wallet(beekeeper: Beekeeper) -> None:
    """Test test_api_create will test beekeeper_api.create will test possibility of creating already existing wallet."""
    # ARRANGE
    wallet = WalletInfo(password="password", name="test_api_create_wallet")
    wallets = (await beekeeper.api.list_wallets()).wallets
    assert len(wallets) == 0, "At the beginning there should be no wallets."

    # ACT & ASSERT
    await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)
    with pytest.raises(CommunicationError, match=f"Wallet with name: '{wallet.name}' already exists"):
        await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)

    # ASSERT
    wallets = (await beekeeper.api.list_wallets()).wallets
    assert len(wallets) == 1, "There should be only one wallet."
    assert wallets[0].name == wallet.name, "After creation there should be only one wallet with given name."


@pytest.mark.parametrize("name", ALLOWED_CHARS)
async def test_api_create_verify_allowed_chars(beekeeper: Beekeeper, name: str) -> None:
    """Test test_api_create will test beekeeper_api.create will check all allowed wallet name chars."""
    # ARRANGE & ACT
    await beekeeper.api.create(wallet_name=name)

    # ASSERT
    wallets = (await beekeeper.api.list_wallets()).wallets
    assert len(wallets) == 1, "There should be one wallet created."


@pytest.mark.parametrize("name", ["Capitalized", "lowercase", ".dot_first", "_underscore_first", "0_number_first"])
async def test_api_create_correct_wallet_name(beekeeper: Beekeeper, name: str) -> None:
    """Test test_api_create will test beekeeper_api.create will create wallet with valid name."""
    # ARRANGE & ACT
    await beekeeper.api.create(wallet_name=name)

    # ASSERT
    wallets = (await beekeeper.api.list_wallets()).wallets
    assert len(wallets) == 1, "There should be one wallet created."


@pytest.mark.parametrize("name", NOT_ALLOWED_CHARS)
async def test_api_create_verify_not_allowed_chars(beekeeper: Beekeeper, name: str) -> None:
    """Test test_api_create will test beekeeper_api.create will check all not allowed wallet name chars."""
    # ARRANGE & ACT & ASSERT
    with pytest.raises(CommunicationError, match="Name of wallet is incorrect."):
        await beekeeper.api.create(wallet_name=name)

    # ASSERT
    wallets = (await beekeeper.api.list_wallets()).wallets
    assert len(wallets) == 0, "There should be no wallets at all."


@pytest.mark.parametrize(
    "name",
    ["!_exclaimation_first", "#_hashtag_first", "8b6#(Uwk", ";*qhKour"],
)
async def test_api_create_not_correct_wallet_name(beekeeper: Beekeeper, name: str) -> None:
    """Test test_api_create will test beekeeper_api.create will try to create wallet with wrong name."""
    # ARRANGE & ACT & ASSERT
    with pytest.raises(CommunicationError, match="Name of wallet is incorrect."):
        await beekeeper.api.create(wallet_name=name)

    # ASSERT
    wallets = (await beekeeper.api.list_wallets()).wallets
    assert len(wallets) == 0, "There should be no wallets at all."
