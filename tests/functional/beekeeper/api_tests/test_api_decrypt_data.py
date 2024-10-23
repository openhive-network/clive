from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive_local_tools.data.models import WalletInfo


async def test_api_decrypt_data(beekeeper: Beekeeper, prepare_wallet: WalletInfo) -> None:
    # PREPARE
    encrypted_content: Final[str] = "bEJXXiFPMfFoWRvBLCfnJKwmngNFCMbSqab5XYE"
    expected_decrypted_content: Final[str] = "some content"

    # ACT
    result = await beekeeper.api.decrypt_data(
        wallet_name=prepare_wallet.name,
        from_public_key=prepare_wallet.public_key.value,
        to_public_key=prepare_wallet.public_key.value,
        encrypted_content=encrypted_content,
    )

    # ASSERT
    assert result.decrypted_content == expected_decrypted_content, "Decrypted buffer has incorrect value."
