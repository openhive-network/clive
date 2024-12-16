from __future__ import annotations

from typing import Final

PROFILE_ENCRYPTION_WALLET_SUFFIX: Final[str] = "_profile_encryption"


def get_encryption_wallet_name(profile_name: str) -> str:
    return f"{profile_name}{PROFILE_ENCRYPTION_WALLET_SUFFIX}"


def is_encryption_wallet_name(wallet_name: str) -> bool:
    return wallet_name.endswith(PROFILE_ENCRYPTION_WALLET_SUFFIX)
