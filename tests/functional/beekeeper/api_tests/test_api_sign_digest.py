from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.exceptions import CommunicationError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive_local_tools.models import WalletInfo

PRIVATE_KEY: Final[str] = "5HwHC7y2WtCL18J9QMqX7awDe1GDsUTg7cfw734m2qFkdMQK92q"
PUBLIC_KEY: Final[str] = "6jACfK3P5xYFJQvavCwz5M8KR5EW3TcmSesArj9LJVGAq85qor"
DIGEST_TO_SIGN: Final[str] = "9B29BA0710AF3918E81D7B935556D7AB205D8A8F5CA2E2427535980C2E8BDAFF"
EXPECTED_SIGNATURE: Final[str] = (
    "1f481d8a164af3f4de957aee236ca1f673825839534912d87e638f0695096718e006ae334f21141ee4a7df5170512fde64faa2123bb2cfc4070539e81b4fab9c6e"
)


async def test_api_sign_digest(beekeeper: Beekeeper, wallet_no_keys: WalletInfo) -> None:
    """Test test_api_sign_digest will test beekeeper_api.sign_digest api call."""
    # ARRANGE
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    # ACT
    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)).signature

    # ASSERT
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."


async def test_api_sign_digest_with_deleted_key(beekeeper: Beekeeper, wallet_no_keys: WalletInfo) -> None:
    """Test test_api_sign_digest will test beekeeper_api.sign_digest will try to sign sigest with key that hase been deleted."""
    # ARRANGE
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)).signature
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."

    await beekeeper.api.remove_key(
        wallet_name=wallet_no_keys.name, password=wallet_no_keys.password, public_key=PUBLIC_KEY
    )

    # ACT & ASSERT
    with pytest.raises(CommunicationError, match=f"Public key {PUBLIC_KEY} not found in unlocked wallets"):
        await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)


async def test_api_sign_digest_with_closed_wallet(beekeeper: Beekeeper, wallet_no_keys: WalletInfo) -> None:
    """Test test_api_sign_digest will test beekeeper_api.sign_digest will try to sign sigest with key in wallet that hase been closed."""
    # ARRANGE
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)).signature
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."

    await beekeeper.api.close(wallet_name=wallet_no_keys.name)

    # ACT & ASSERT
    with pytest.raises(CommunicationError, match=f"Public key {PUBLIC_KEY} not found in unlocked wallets"):
        await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)


async def test_api_sign_digest_with_deleted_wallet(beekeeper: Beekeeper, wallet_no_keys: WalletInfo) -> None:
    """Test test_api_sign_digest will test beekeeper_api.sign_digest will try to sign digest with key in wallet that has been deleted."""
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
    # ARRANGE
    """Test test_api_sign_digest will test beekeeper_api.sign_digest will try to sign digest with key in wallet that has been locked."""
    await beekeeper.api.import_key(wallet_name=wallet_no_keys.name, wif_key=PRIVATE_KEY)

    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)).signature
    assert signature == EXPECTED_SIGNATURE, "Signatures should match."

    await beekeeper.api.lock(wallet_name=wallet_no_keys.name)

    # ACT & ASSERT
    with pytest.raises(CommunicationError, match=f"Public key {PUBLIC_KEY} not found in unlocked wallets"):
        await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=PUBLIC_KEY)
