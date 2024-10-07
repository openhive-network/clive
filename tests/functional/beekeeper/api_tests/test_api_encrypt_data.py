from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive_local_tools.data.models import WalletInfo


async def test_api_encrypt_data(beekeeper: Beekeeper, prepare_beekeeper_wallet_with_session: WalletInfo) -> None:
    # PREPARE
    content: Final[str] = "some content"
    nonce: Final[int] = 13
    expected_encrypted_content: Final[str] = "bEJXXiFPMfFoWRvBLCfnJKwmngNFCMbSqab5XYE"

    # ACT
    result = await beekeeper.api.encrypt_data(
        wallet_name=prepare_beekeeper_wallet_with_session.name,
        from_public_key=prepare_beekeeper_wallet_with_session.public_key.value,
        to_public_key=prepare_beekeeper_wallet_with_session.public_key.value,
        content=content,
        nonce=nonce,
    )

    # ASSERT
    assert result.encrypted_content == expected_encrypted_content, "Encrypted buffer has incorrect value."
