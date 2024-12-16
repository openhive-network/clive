from __future__ import annotations

from typing import Final

PROFILE_ENCRYPTION_WALLET_SUFFIX: Final[str] = "_profile_encryption"
PROFILE_FILENAME_SUFFIX: Final[str] = ".profile"


def get_encryption_wallet_name(profile_name: str) -> str:
    return f"{profile_name}{PROFILE_ENCRYPTION_WALLET_SUFFIX}"


def is_encryption_wallet_name(wallet_name: str) -> bool:
    return wallet_name.endswith(PROFILE_ENCRYPTION_WALLET_SUFFIX)


def get_profile_filename(profile_name: str) -> str:
    return f"{profile_name}{PROFILE_FILENAME_SUFFIX}"


def is_profile_filename(file_name: str) -> bool:
    return file_name.endswith(PROFILE_FILENAME_SUFFIX)
