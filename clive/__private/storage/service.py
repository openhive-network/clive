from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from clive.__private.core.constants.profile import PROFILE_FILENAME_EXTENSION
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.storage.model import ProfileStorageModel, calculate_storage_model_revision
from clive.__private.storage.runtime_to_storage_converter import RuntimeToStorageConverter
from clive.__private.storage.storage_to_runtime_converter import StorageToRuntimeConverter
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.encryption import EncryptionService
    from clive.__private.core.profile import Profile


class PersistentStorageServiceError(CliveError):
    """Base class for all PersistentStorageService exceptions."""


class ProfileDoesNotExistsError(PersistentStorageServiceError):
    def __init__(self, profile_name: str) -> None:
        self.profile_name = profile_name
        self.message = f"Profile `{profile_name}` does not exist."
        super().__init__(self.message)


class ProfileAlreadyExistsError(PersistentStorageServiceError):
    def __init__(self, profile_name: str, existing_profile_names: Iterable[str] | None = None) -> None:
        self.profile_name = profile_name
        self.existing_profile_names = list(existing_profile_names) if existing_profile_names is not None else []
        detail = f", different than {self.existing_profile_names}." if existing_profile_names else "."
        self.message = f"Profile `{self.profile_name}` already exists. Please choose another name{detail}"
        super().__init__(self.message)


class NoDefaultProfileToLoadError(PersistentStorageServiceError):
    def __init__(self) -> None:
        self.message = "No default profile to load."
        super().__init__(self.message)


class PersistentStorageService:
    def __init__(self, encryption_service: EncryptionService) -> None:
        self._encryption_service = encryption_service
        self._encrypted_storage: dict[str, str] = self._load_storage()

    @property
    def encrypted_storage(self) -> dict[str, str]:
        return self._encrypted_storage

    def save_storage(self) -> None:
        versioned_storage_dir = self._get_storage_versioned_directory()
        versioned_storage_dir.mkdir(parents=True, exist_ok=True)
        for profile_name, encrypted_profile in self.encrypted_storage.items():
            (versioned_storage_dir / f"{profile_name}{PROFILE_FILENAME_EXTENSION}").write_text(encrypted_profile)
        self._create_current_storage_symlink()

    async def _save_profile(self, profile: Profile) -> None:
        """
        Save profile to the storage.

        Args:
        ----
            profile: Profile to be saved.

        Raises:
        ------
            ProfileAlreadyExistsError: If given profile is newly created and profile with that name already exists,
                it could not be saved, that would overwrite other profile.
        """
        self._raise_if_profile_with_name_already_exists_on_first_save(profile)
        profile.unset_is_newly_created()

        model = RuntimeToStorageConverter(profile).create_storage_model()
        serialized = self._serialize_profile_model(model)
        encrypted_content = await self._encryption_service.encrypt(serialized)

        self.encrypted_storage[model.name] = encrypted_content
        self.save_storage()

    async def load_profile(self, profile_name: str | None = None) -> Profile:
        """
        Load profile with the given name from the storage.

        Args:
        ----
            profile_name: Name of the profile to be loaded. If not provided, default profile will be loaded.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be loaded
            NoDefaultProfileToLoadError: If no default profile is set, it could not be loaded.
        """
        profile_name_ = profile_name or self._encryption_service.profile_name
        self._raise_if_profile_not_stored(profile_name_)
        encrypted_content = self.encrypted_storage[profile_name_]
        serialized = await self._encryption_service.decrypt(encrypted_content)
        model = self._deserialize_profile_model(serialized)
        return StorageToRuntimeConverter(model).create_profile()

    @classmethod
    def remove_profile(cls, profile_name: str) -> None:
        """
        Remove profile with the given name from the storage.

        Args:
        ----
            profile_name: Name of the profile to be removed.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be removed.
        """
        cls._raise_if_profile_not_stored(profile_name)
        versioned_storage_dir = cls._get_storage_versioned_directory()
        (versioned_storage_dir / f"{profile_name}{PROFILE_FILENAME_EXTENSION}").unlink()

    @classmethod
    def list_stored_profile_names(cls) -> list[str]:
        """List all stored profile names sorted alphabetically."""
        versioned_storage_dir = cls._get_storage_versioned_directory()
        if not versioned_storage_dir.exists():
            return []
        return sorted(
            file.stem
            for file in versioned_storage_dir.iterdir()
            if file.is_file() and file.suffix == PROFILE_FILENAME_EXTENSION
        )

    @classmethod
    def get_default_profile_name(cls) -> str:
        """
        Get the profile name of default profile stored in the storage.

        Raises:  # noqa: D406
        ------
            NoDefaultProfileToLoadError: If no default profile is set, it could not be loaded.
        """
        profiles = cls.list_stored_profile_names()
        if len(profiles) != 1:
            raise NoDefaultProfileToLoadError
        return profiles[0]

    @classmethod
    def is_profile_stored(cls, profile_name: str) -> bool:
        return profile_name in cls.list_stored_profile_names()

    @classmethod
    def _get_storage_directory(cls) -> Path:
        return safe_settings.data_path / "data"

    @classmethod
    def _get_storage_versioned_directory(cls) -> Path:
        """Get the directory where the storage file is stored in a versioned way."""
        revision = calculate_storage_model_revision()
        return cls._get_storage_directory() / revision

    def _create_current_storage_symlink(self) -> None:
        versioned_storage_dir = self._get_storage_versioned_directory()
        symlink_dir = self._get_storage_directory() / "current"

        if symlink_dir.resolve() == versioned_storage_dir:
            logger.debug("Current storage symlink already points to the current version. Skipping symlink creation.")
            return

        symlink_dir.unlink(missing_ok=True)
        symlink_dir.symlink_to(versioned_storage_dir, target_is_directory=True)

    @classmethod
    def _load_storage(cls) -> dict[str, str]:
        versioned_storage_dir = cls._get_storage_versioned_directory()
        versioned_storage_dir.mkdir(parents=True, exist_ok=True)
        encrypted_storage: dict[str, str] = {}
        for file in versioned_storage_dir.iterdir():
            if file.is_file() and file.suffix == PROFILE_FILENAME_EXTENSION:
                profile_name = file.stem
                encrypted_storage[profile_name] = file.read_text()
        return encrypted_storage

    @classmethod
    def _serialize_profile_model(cls, storage: ProfileStorageModel) -> str:
        return storage.json(indent=4)

    @classmethod
    def _deserialize_profile_model(cls, storage_serialized: str) -> ProfileStorageModel:
        return ProfileStorageModel.parse_raw(storage_serialized)

    @classmethod
    def _raise_if_profile_not_stored(cls, profile_name: str) -> None:
        if not cls.is_profile_stored(profile_name):
            raise ProfileDoesNotExistsError(profile_name)

    def _raise_if_profile_with_name_already_exists_on_first_save(self, profile: Profile) -> None:
        profile_name = profile.name
        is_newly_created = profile.is_newly_created
        existing_profile_names = self.list_stored_profile_names()

        if is_newly_created and profile_name in existing_profile_names:
            raise ProfileAlreadyExistsError(profile_name, existing_profile_names)
