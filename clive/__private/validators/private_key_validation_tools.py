from __future__ import annotations

from typing import TYPE_CHECKING

from wax.exceptions.chain_errors import PrivateKeyDetectedInMemoError

if TYPE_CHECKING:
    from clive.__private.core.world import World


def contains_private_key(content: str, world: World) -> bool:
    """
    Check if the given content contains a private key for any of the tracked accounts.

    Args:
        content: The text content to scan for private keys.
        world: The world object containing wax_interface and profile with tracked accounts.

    Returns:
        True if a private key is detected in the content, False otherwise.
    """
    for account in world.profile.accounts.tracked:
        authority = account.data.authority
        try:
            world.wax_interface.scan_text_for_matching_private_keys(
                content=content,
                account=account.name,
                account_authorities=authority.wax_authorities,
                memo_key=authority.memo_key,
            )
        except PrivateKeyDetectedInMemoError:
            return True
    return False
