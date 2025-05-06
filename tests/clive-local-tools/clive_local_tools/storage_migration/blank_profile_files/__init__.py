from __future__ import annotations

from typing import Final

FUTURE_NOT_SUPPORTED_YET_VERSION: Final[str] = "future_not_supported_yet_version"
LEGACY_BACKUP: Final[str] = "legacy_backup"
LEGACY_PROFILE: Final[str] = "legacy_profile"
VERSIONED_BACKUP: Final[str] = "versioned_backup"
VERSIONED_OLDER_AND_NEWER_PROFILE: Final[str] = "versioned_older_and_newer_profile"
VERSIONED_PROFILE: Final[str] = "versioned_profile"
VERSIONED_PROFILE_AND_OLDER_BACKUP: Final[str] = "versioned_profile_and_older_backup"

BLANK_PROFILES: Final[tuple[str, ...]] = (
    LEGACY_PROFILE,
    VERSIONED_OLDER_AND_NEWER_PROFILE,
    VERSIONED_PROFILE,
    VERSIONED_PROFILE_AND_OLDER_BACKUP,
)
