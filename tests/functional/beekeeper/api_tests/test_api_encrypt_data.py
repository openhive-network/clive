from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.keys import PrivateKeyAliased
    from clive_local_tools.data.models import WalletInfo


async def test_api_encrypt_data(
    beekeeper: Beekeeper, wallet_working_account_key: WalletInfo, working_account_private_key: PrivateKeyAliased
) -> None:
    # PREPARE
    content: Final[str] = "some content"
    nonce: Final[int] = 13
    expected_encrypted_content: Final[str] = "bEJXXiFPMfFoWRvBLCfnJKwmngNFCMbSqab5XYE"

    # ACT
    result = await beekeeper.api.encrypt_data(
        wallet_name=wallet_working_account_key.name,
        from_public_key=working_account_private_key.calculate_public_key().value,
        to_public_key=working_account_private_key.calculate_public_key().value,
        content=content,
        nonce=nonce,
    )

    # ASSERT
    assert result.encrypted_content == expected_encrypted_content, "Encrypted buffer has incorrect value."
