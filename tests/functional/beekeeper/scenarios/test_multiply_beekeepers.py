from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.beekeeper import Beekeeper
from clive_local_tools.models import Keys, WalletInfo

if TYPE_CHECKING:
    from pathlib import Path

DIGEST_TO_SIGN: Final[str] = "9B29BA0710AF3918E81D7B935556D7AB205D8A8F5CA2E2427535980C2E8BDAFF"


async def test_multiply_beekeepeer_same_storage(tmp_path: Path) -> None:
    """Test test_multiply_beekeepeer_same_storage will check, if it is possible to run multiple instances of beekeepers pointing to the same storage."""
    # ARRANGE
    same_storage = tmp_path / "same_storage"
    same_storage.mkdir()

    # ACT
    _ = await Beekeeper().launch(wallet_dir=same_storage)

    # Now we get assert because of https://gitlab.syncad.com/hive/hive/-/issues/622
    # Related clive:
    #   https://gitlab.syncad.com/hive/clive/-/issues/102
    # ACT & ASSERT
    with pytest.raises(AssertionError):
        _ = await Beekeeper().launch(wallet_dir=same_storage)


async def simple_flow(beekeeper: Beekeeper) -> None:
    """Function `simple_flow` will simulate a simple work flow on given beekeeper."""
    wallet = WalletInfo(name="wallet", password="password", keys=Keys(1))
    async with beekeeper.with_new_session():
        await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)
        wallets = (await beekeeper.api.list_wallets()).wallets
        assert wallet.name == wallets[0].name, f"There should be only one wallet, with {wallet.name} name."

        await beekeeper.api.import_key(wallet_name=wallet.name, wif_key=wallet.private_key.value)
        keys = (await beekeeper.api.get_public_keys()).keys
        assert (
            wallet.public_key.value == keys[0].public_key
        ), f"There should be only one public key {wallet.public_key.value}."

        await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=wallet.public_key.value)


async def test_multiply_beekeepeer_different_storage(tmp_path: Path) -> None:
    """Test test_multiply_beekeepeer_different_storage will check, if it is possible to run multiple instances of beekeepers pointing to the different storage."""
    # ARRANGE
    bk1_path = tmp_path / "bk1"
    bk1_path.mkdir()

    bk2_path = tmp_path / "bk2"
    bk2_path.mkdir()

    # ACT
    bk1 = await Beekeeper().launch(wallet_dir=bk1_path)
    bk2 = await Beekeeper().launch(wallet_dir=bk2_path)

    # ASSERT
    await asyncio.gather(*[simple_flow(bk1), simple_flow(bk2)])
