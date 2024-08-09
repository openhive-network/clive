from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from clive.__private.settings import safe_settings
from clive.__private.storage.model import PersistentStorageModel, ProfileStorageModel
from clive.__private.storage.runtime_to_storage_converter import RuntimeToStorageConverter
from clive.__private.storage.storage_to_runtime_converter import StorageToRuntimeConverter
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.profile_data import ProfileData


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
    @classmethod
    def save_storage(cls, storage: PersistentStorageModel) -> None:
        storage_path = cls._get_storage_filepath()
        serialized_storage = cls._serialize_storage_model(storage)

        # create data directory if it doesn't exist
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        storage_path.write_text(serialized_storage)

    @classmethod
    def load_storage(cls) -> PersistentStorageModel:
        storage_path = cls._get_storage_filepath()
        if not storage_path.is_file():
            return PersistentStorageModel()

        storage_serialized = storage_path.read_text()
        return cls._deserialize_storage_model(storage_serialized)

    @classmethod
    def save_profile(cls, profile: ProfileData) -> None:
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
        storage = cls.load_storage()

        cls._raise_if_profile_with_name_already_exists_on_first_save(profile, storage)
        profile.unset_is_newly_created()

        model = RuntimeToStorageConverter(profile).create_storage_model()

        if not cls.is_default_profile_set(storage):
            # set first profile as default when no default set yet
            cls._set_default_profile(model.name, storage)

        # remove old profile if exists
        storage.profiles = cls._remove_profile_storage_model_by_name(model.name, storage.profiles)
        storage.profiles.append(model)
        cls.save_storage(storage)

    @classmethod
    def load_profile(cls, profile_name: str | None = None) -> ProfileData:
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
        storage = cls.load_storage()
        profile_name_ = profile_name if profile_name is not None else cls.get_default_profile_name(storage)
        cls._raise_if_profile_not_stored(profile_name_, storage)
        profile_storage_model = cls._find_profile_storage_model_by_name(profile_name_, storage.profiles)
        return StorageToRuntimeConverter(profile_storage_model).create_profile()

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
        storage = cls.load_storage()
        cls._raise_if_profile_not_stored(profile_name, storage)
        storage.profiles = cls._remove_profile_storage_model_by_name(profile_name, storage.profiles)
        cls.save_storage(storage)

    @classmethod
    def list_stored_profile_names(cls, storage: PersistentStorageModel | None = None) -> list[str]:
        """List all stored profile names sorted alphabetically."""
        storage = cls._get_storage(storage)
        return sorted(profile.name for profile in storage.profiles)

    @classmethod
    def get_default_profile_name(cls, storage: PersistentStorageModel | None = None) -> str:
        """
        Get the profile name of default profile stored in the storage.

        Args:
        ----
            storage: Storage model to be used. If not provided, storage will be loaded from the disk.

        Raises:
        ------
            NoDefaultProfileToLoadError: If no default profile is set, it could not be loaded.
        """
        storage = cls._get_storage(storage)
        cls._raise_if_no_default_profile_is_set(storage)
        assert storage.default_profile is not None, "Default profile must be set if no error was raised."
        return storage.default_profile

    @classmethod
    def set_default_profile(cls, profile_name: str) -> None:
        """
        Set profile as default.

        Args:
        ----
            profile_name: Name of the profile to be set as default.
            storage: Storage model to be used. If not provided, storage will be loaded from the disk.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be set as default.
        """
        storage = cls._get_storage()
        cls._raise_if_profile_not_stored(profile_name, storage)
        cls._set_default_profile(profile_name, storage)
        cls.save_storage(storage)

    @classmethod
    def is_profile_stored(cls, profile_name: str, storage: PersistentStorageModel | None = None) -> bool:
        storage = cls._get_storage(storage)
        return profile_name in cls.list_stored_profile_names(storage)

    @classmethod
    def is_default_profile_set(cls, storage: PersistentStorageModel | None = None) -> bool:
        storage = cls._get_storage(storage)
        return storage.default_profile is not None

    @classmethod
    def _get_storage_filepath(cls) -> Path:
        return safe_settings.data_path / "data/profiles.json"

    @classmethod
    def _get_storage(cls, storage: PersistentStorageModel | None = None) -> PersistentStorageModel:
        return cls.load_storage() if storage is None else storage

    @classmethod
    def _set_default_profile(cls, profile_name: str, storage: PersistentStorageModel) -> None:
        storage.default_profile = profile_name

    @classmethod
    def _find_profile_storage_model_by_name(
        cls, profile_name: str, profiles: Iterable[ProfileStorageModel]
    ) -> ProfileStorageModel:
        """
        Find profile storage model by name in the given container of profiles.

        Args:
        ----
            profile_name: Name of the profile to be found.
            profiles: Container of profiles to search in.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be found.
        """
        profile_storage_model = next((profile for profile in profiles if profile.name == profile_name), None)
        if profile_storage_model is None:
            raise ProfileDoesNotExistsError(profile_name)
        return profile_storage_model

    @classmethod
    def _remove_profile_storage_model_by_name(
        cls, profile_name: str, profiles: Iterable[ProfileStorageModel]
    ) -> list[ProfileStorageModel]:
        return [profile for profile in profiles if profile.name != profile_name]

    @classmethod
    def _serialize_storage_model(cls, storage: PersistentStorageModel) -> str:
        return storage.json(indent=4)

    @classmethod
    def _deserialize_storage_model(cls, storage_serialized: str) -> PersistentStorageModel:
        return PersistentStorageModel.parse_raw(storage_serialized)

    @classmethod
    def _raise_if_no_default_profile_is_set(cls, storage: PersistentStorageModel) -> None:
        if not cls.is_default_profile_set(storage):
            raise NoDefaultProfileToLoadError

    @classmethod
    def _raise_if_profile_not_stored(cls, profile_name: str, storage: PersistentStorageModel | None = None) -> None:
        if not cls.is_profile_stored(profile_name, storage):
            raise ProfileDoesNotExistsError(profile_name)

    @classmethod
    def _raise_if_profile_with_name_already_exists_on_first_save(
        cls, profile: ProfileData, storage: PersistentStorageModel
    ) -> None:
        profile_name = profile.name
        is_newly_created = profile.is_newly_created
        existing_profile_names = cls.list_stored_profile_names(storage)

        if is_newly_created and profile_name in existing_profile_names:
            raise ProfileAlreadyExistsError(profile_name, existing_profile_names)
