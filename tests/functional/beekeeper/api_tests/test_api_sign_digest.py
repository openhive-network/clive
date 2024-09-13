from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.keys import PrivateKey
from clive.exceptions import CommunicationError
from clive_local_tools.beekeeper.constants import DIGEST_TO_SIGN

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive_local_tools.data.models import WalletInfo

PRIVATE_KEY_MODEL: Final[PrivateKey] = PrivateKey(value="5HwHC7y2WtCL18J9QMqX7awDe1GDsUTg7cfw734m2qFkdMQK92q")
PRIVATE_KEY: Final[str] = PRIVATE_KEY_MODEL.value
PUBLIC_KEY: Final[str] = PRIVATE_KEY_MODEL.calculate_public_key().value
EXPECTED_SIGNATURE: Final[str] = (
    "20e25ced7114f8edc36127453c97b2b78884611896701a02b018d977e707ca7a1e4c82a9997a520890b35ed1ecb87ddd66190735e126e3f2b2329d12059af1f3e9"
)


@pytest.mark.parametrize("explicit_wallet_name", [False, True])
async def test_api_sign_digest(beekeeper: Beekeeper, wallet_no_keys: WalletInfo, explicit_wallet_name: str) -> None:
    # ARRANGE
    explicit_wallet_name_param = {"wallet_name": wallet_no_keys.name} if explicit_wallet_name else {}
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    # ACT
    signature = (
        await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY, **explicit_wallet_name_param)
    ).signature

    # ASSERT
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."


async def test_api_sign_digest_with_different_wallet_name(beekeeper: Beekeeper, wallet_no_keys: WalletInfo) -> None:
    # ARRANGE
    not_existing_wallet_name = "not-existing"
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    # ACT & ASSERT
    with pytest.raises(
        CommunicationError, match=f"Public key {PUBLIC_KEY} not found in {not_existing_wallet_name} wallet"
    ):
        await beekeeper.api.sign_digest(
            sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY, wallet_name=not_existing_wallet_name
        )


async def test_api_sign_digest_with_deleted_key(beekeeper: Beekeeper, wallet_no_keys: WalletInfo) -> None:
    """Will try to sign digest with key that hase been deleted."""
    # ARRANGE
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)).signature
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."

    await beekeeper.api.remove_key(wallet_name=wallet_no_keys.name, public_key=PUBLIC_KEY)

    # ACT & ASSERT
    with pytest.raises(CommunicationError, match=f"Public key {PUBLIC_KEY} not found in unlocked wallets"):
        await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)


async def test_api_sign_digest_with_closed_wallet(beekeeper: Beekeeper, wallet_no_keys: WalletInfo) -> None:
    """Will try to sign digest with key in wallet that hase been closed."""
    # ARRANGE
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)).signature
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."

    await beekeeper.api.close(wallet_name=wallet_no_keys.name)

    # ACT & ASSERT
    with pytest.raises(CommunicationError, match=f"Public key {PUBLIC_KEY} not found in unlocked wallets"):
        await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)


async def test_api_sign_digest_with_deleted_wallet(beekeeper: Beekeeper, wallet_no_keys: WalletInfo) -> None:
    """Will try to sign digest with key in wallet that has been deleted."""
    # ARRANGE
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)).signature
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."

    # ACT
    wallet_path = beekeeper.get_wallet_dir() / f"{wallet_no_keys.name}.wallet"
    assert wallet_path.exists() is True, "Wallet should exists."
    wallet_path.unlink()
    assert wallet_path.exists() is False, "Wallet should not exists."

    # ASSERT
    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)).signature
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."


async def test_api_sign_digest_with_locked_wallet(beekeeper: Beekeeper, wallet_no_keys: WalletInfo) -> None:
    """Will try to sign digest with key in wallet that has been locked."""
    # ARRANGE
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)).signature
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."

    await beekeeper.api.lock(wallet_name=wallet_no_keys.name)

    # ACT & ASSERT
    with pytest.raises(CommunicationError, match=f"Public key {PUBLIC_KEY} not found in unlocked wallets"):
        await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)
