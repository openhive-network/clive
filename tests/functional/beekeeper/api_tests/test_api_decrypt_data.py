from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.keys import PrivateKeyAliased
    from clive_local_tools.data.models import WalletInfo


async def test_api_decrypt_data(
    beekeeper: Beekeeper, wallet_working_account_key: WalletInfo, working_account_private_key: PrivateKeyAliased
) -> None:
    # PREPARE
    encrypted_content: Final[str] = "Kf4KJv2p18q5Rjy3SzprWr9Zo42NiLEpfX8q3DX8WGUJT8G8xcaeoJRS3JVKC"
    expected_decrypted_content: Final[str] = "some content decrypted"

    # ACT
    result = await beekeeper.api.decrypt_data(
        wallet_name=wallet_working_account_key.name,
        from_public_key=working_account_private_key.calculate_public_key().value,
        to_public_key=working_account_private_key.calculate_public_key().value,
        encrypted_content=encrypted_content,
    )

    # ASSERT
    assert result.decrypted_content == expected_decrypted_content, "Decrypted buffer has incorrect value."
