from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Iterable

from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.storage.model import PersistentStorageModel, ProfileStorageModel, calculate_storage_model_revision
from clive.__private.storage.runtime_to_storage_converter import RuntimeToStorageConverter
from clive.__private.storage.storage_to_runtime_converter import StorageToRuntimeConverter
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from pathlib import Path

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
    def __init__(self) -> None:
        self._cached_storage: PersistentStorageModel | None = None

    @property
    def cached_storage(self) -> PersistentStorageModel:
        if self._cached_storage is None:
            self._cached_storage = self._load_storage()
        return self._cached_storage

    def save_storage(self) -> None:
        versioned_storage_dir = self._get_storage_versioned_directory()
        storage_path = self._get_storage_filepath()
        serialized_storage = self._serialize_storage_model(self.cached_storage)

        # create data directory if it doesn't exist
        versioned_storage_dir.mkdir(parents=True, exist_ok=True)

        self._create_current_storage_symlink()

        storage_path.write_text(serialized_storage)

    def save_profile(self, profile: Profile) -> None:
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

        if not self.is_default_profile_set():
            # set first profile as default when no default set yet
            self._set_default_profile(model.name)

        self._remove_profile_storage_model_by_name(model.name)  # remove old profile if exists
        self.cached_storage.profiles.append(model)
        self.save_storage()

    def load_profile(self, profile_name: str | None = None) -> Profile:
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
        profile_name_ = profile_name if profile_name is not None else self.get_default_profile_name()
        self._raise_if_profile_not_stored(profile_name_)
        profile_storage_model = self._find_profile_storage_model_by_name(profile_name_)

        return StorageToRuntimeConverter(profile_storage_model).create_profile()

    def remove_profile(self, profile_name: str) -> None:
        """
        Remove profile with the given name from the storage.

        Args:
        ----
            profile_name: Name of the profile to be removed.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be removed.
        """
        self._raise_if_profile_not_stored(profile_name)
        self._remove_profile_storage_model_by_name(profile_name)
        with contextlib.suppress(NoDefaultProfileToLoadError):
            if profile_name == self.get_default_profile_name():
                self._unset_default_profile()
        self.save_storage()

    def list_stored_profile_names(self) -> list[str]:
        """List all stored profile names sorted alphabetically."""
        return sorted(profile.name for profile in self.cached_storage.profiles)

    def get_default_profile_name(self) -> str:
        """
        Get the profile name of default profile stored in the storage.

        Raises:  # noqa: D406
        ------
            NoDefaultProfileToLoadError: If no default profile is set, it could not be loaded.
        """
        self._raise_if_no_default_profile_is_set()
        storage = self.cached_storage
        assert storage.default_profile is not None, "Default profile must be set if no error was raised."
        return storage.default_profile

    def set_default_profile(self, profile_name: str) -> None:
        """
        Set profile as default.

        Args:
        ----
            profile_name: Name of the profile to be set as default.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be set as default.
        """
        self._raise_if_profile_not_stored(profile_name)
        self._set_default_profile(profile_name)
        self.save_storage()

    def is_profile_stored(self, profile_name: str) -> bool:
        return profile_name in self.list_stored_profile_names()

    def is_default_profile_set(self) -> bool:
        return self.cached_storage.default_profile is not None

    @classmethod
    def _get_storage_directory(cls) -> Path:
        return safe_settings.data_path / "data"

    @classmethod
    def _get_storage_versioned_directory(cls) -> Path:
        """Get the directory where the storage file is stored in a versioned way."""
        revision = calculate_storage_model_revision()
        return cls._get_storage_directory() / revision

    @classmethod
    def _get_storage_filepath(cls) -> Path:
        return cls._get_storage_versioned_directory() / "profiles.json"

    def _create_current_storage_symlink(self) -> None:
        versioned_storage_dir = self._get_storage_versioned_directory()
        symlink_dir = self._get_storage_directory() / "current"

        if symlink_dir.resolve() == versioned_storage_dir:
            logger.debug("Current storage symlink already points to the current version. Skipping symlink creation.")
            return

        symlink_dir.unlink(missing_ok=True)
        symlink_dir.symlink_to(versioned_storage_dir, target_is_directory=True)

    def _load_storage(self) -> PersistentStorageModel:
        storage_path = self._get_storage_filepath()
        if not storage_path.is_file():
            return PersistentStorageModel()

        storage_serialized = storage_path.read_text()
        return self._deserialize_storage_model(storage_serialized)

    def _set_default_profile(self, profile_name: str) -> None:
        self.cached_storage.default_profile = profile_name

    def _unset_default_profile(self) -> None:
        self.cached_storage.default_profile = None

    def _find_profile_storage_model_by_name(self, profile_name: str) -> ProfileStorageModel:
        """
        Find profile storage model by name in the given container of profiles.

        Args:
        ----
            profile_name: Name of the profile to be found.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be found.
        """
        profiles = self.cached_storage.profiles
        profile_storage_model = next((profile for profile in profiles if profile.name == profile_name), None)
        if profile_storage_model is None:
            raise ProfileDoesNotExistsError(profile_name)
        return profile_storage_model

    def _remove_profile_storage_model_by_name(self, profile_name: str) -> None:
        storage = self.cached_storage
        old_profiles = storage.profiles
        new_profiles = [profile for profile in old_profiles if profile.name != profile_name]
        storage.profiles = new_profiles

    @classmethod
    def _serialize_storage_model(cls, storage: PersistentStorageModel) -> str:
        return storage.json(indent=4)

    @classmethod
    def _deserialize_storage_model(cls, storage_serialized: str) -> PersistentStorageModel:
        return PersistentStorageModel.parse_raw(storage_serialized)

    def _raise_if_no_default_profile_is_set(self) -> None:
        if not self.is_default_profile_set():
            raise NoDefaultProfileToLoadError

    def _raise_if_profile_not_stored(self, profile_name: str) -> None:
        if not self.is_profile_stored(profile_name):
            raise ProfileDoesNotExistsError(profile_name)

    def _raise_if_profile_with_name_already_exists_on_first_save(self, profile: Profile) -> None:
        profile_name = profile.name
        is_newly_created = profile.is_newly_created
        existing_profile_names = self.list_stored_profile_names()

        if is_newly_created and profile_name in existing_profile_names:
            raise ProfileAlreadyExistsError(profile_name, existing_profile_names)
