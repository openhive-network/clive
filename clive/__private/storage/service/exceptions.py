from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


class PersistentStorageServiceError(CliveError):
    """Base class for all PersistentStorageService exceptions."""


class ProfileDoesNotExistsError(PersistentStorageServiceError):
    def __init__(self, profile_name: str) -> None:
        self.profile_name = profile_name
        self.message = f"Profile `{profile_name}` does not exist."
        super().__init__(self.message)


class MultipleProfileVersionsError(PersistentStorageServiceError):
    def __init__(self, profile_name: str) -> None:
        self.profile_name = profile_name
        self.message = f"Multiple versions or backups of profile `{profile_name}` exist."
        super().__init__(self.message)


class ModelDoesNotExistsError(PersistentStorageServiceError):
    def __init__(self, path: Path) -> None:
        self.message = f"Model not found for profile stored at `{path}`."
        super().__init__(self.message)


class ProfileAlreadyExistsError(PersistentStorageServiceError):
    def __init__(self, profile_name: str, existing_profile_names: Iterable[str] | None = None) -> None:
        self.profile_name = profile_name
        self.existing_profile_names = list(existing_profile_names) if existing_profile_names is not None else []
        detail = f", different than {self.existing_profile_names}." if existing_profile_names else "."
        self.message = f"Profile `{self.profile_name}` already exists. Please choose another name{detail}"
        super().__init__(self.message)


class ProfileEncryptionError(PersistentStorageServiceError):
    """
    Raised when there is an issue with encryption or decryption of the profile e.g. during save or load.

    Attributes:
        MESSAGE: A default error message indicating the failure reason.
    """

    MESSAGE: Final[str] = (
        "Profile encryption failed. Maybe the wallet is locked, or communication with the beekeeper failed?"
    )

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)
