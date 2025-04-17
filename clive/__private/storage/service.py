from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command_encryption import CommandRequiresUnlockedEncryptionWalletError
from clive.__private.core.commands.decrypt import CommandDecryptError
from clive.__private.core.commands.encrypt import CommandEncryptError
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.storage.model import ProfileStorageBase, apply_all_migrations
from clive.__private.storage.runtime_to_storage_converter import RuntimeToStorageConverter
from clive.__private.storage.storage_to_runtime_converter import StorageToRuntimeConverter
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from clive.__private.core.encryption import EncryptionService
    from clive.__private.core.profile import Profile
    from clive.__private.storage.model import ProfileStorageModel


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
        self.message = f"Model not found for profile stored at `{path.name}`."
        super().__init__(self.message)


class ProfileAlreadyExistsError(PersistentStorageServiceError):
    def __init__(self, profile_name: str, existing_profile_names: Iterable[str] | None = None) -> None:
        self.profile_name = profile_name
        self.existing_profile_names = list(existing_profile_names) if existing_profile_names is not None else []
        detail = f", different than {self.existing_profile_names}." if existing_profile_names else "."
        self.message = f"Profile `{self.profile_name}` already exists. Please choose another name{detail}"
        super().__init__(self.message)


class ProfileEncryptionError(PersistentStorageServiceError):
    """Raised when there is an issue with encryption or decryption of the profile e.g. during save or load."""

    MESSAGE: Final[str] = (
        "Profile encryption failed. Maybe the wallet is locked, or communication with the beekeeper failed?"
    )

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class PersistentStorageService:
    BACKUP_FILENAME_SUFFIX: Final[str] = ".backup"
    PROFILE_FILENAME_SUFFIX: Final[str] = ".profile"
    FIRST_REVISION: Final[str] = "c600278a"

    @dataclass(frozen=True)
    class ProfileNameModel:
        name: str
        model_cls: type[ProfileStorageBase]

        def version(self) -> int:
            return self.model_cls.get_this_version_number()

    type ProfileNameModelToPath = dict[ProfileNameModel, Path]

    def __init__(self, encryption_service: EncryptionService) -> None:
        self._encryption_service = encryption_service

    async def save_profile(self, profile: Profile) -> None:
        """
        Save profile to the storage.

        Args:
        ----
            profile: Profile to be saved.

        Raises:
        ------
            ProfileAlreadyExistsError: If given profile is newly created and profile with that name already exists,
                it could not be saved, that would overwrite other profile.
            ProfileEncryptionError: If profile could not be saved e.g. due to beekeeper wallet being locked
                or communication with beekeeper failed.
        """
        self._raise_if_profile_with_name_already_exists_on_first_save(profile)
        if not profile.should_be_saved:
            logger.debug("Saving profile skipped... Looks like was explicitly skipped or hash didn't changed.")
            return

        profile_model = RuntimeToStorageConverter(profile).create_storage_model()
        await self._save_profile_model(profile_model)
        profile._update_hash_of_stored_profile()

    async def load_profile(self, profile_name: str) -> Profile:
        """
        Load profile with the given name from the storage.

        Args:
        ----
            profile_name: Name of the profile to be loaded.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be loaded
            ProfileEncryptionError: If profile could not be loaded e.g. due to beekeeper wallet being locked
                or communication with beekeeper failed.
        """
        self._raise_if_profile_not_stored(profile_name)
        profile_storage_model = await self._find_or_migrate_profile_storage_model_by_name(profile_name)

        profile = StorageToRuntimeConverter(profile_storage_model).create_profile()
        profile._update_hash_of_stored_profile()
        return profile

    @classmethod
    def delete_profile(cls, profile_name: str, *, force: bool = False) -> None:
        """
        Remove profile with the given name from the storage.

        Args:
        ----
            profile_name: Name of the profile to be removed, removes all storage versions.
            force: If True, remove all profile versions, also not migrated/backed-up.
                If False and multiple versions exist, raise error.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be removed.
            MultipleProfileVersionsError: If multiple versions / back-ups of profile exist and force is False.
        """
        if not force:
            cls._raise_if_profile_not_stored(profile_name)
        filepaths = cls._get_storage_filepaths()
        backup_filepaths = cls._get_backup_filepaths()

        to_remove = [path for key, path in filepaths.items() if key.name == profile_name]
        to_remove.extend([path for key, path in backup_filepaths.items() if key.name == profile_name])
        if not force and len(to_remove) > 1:
            raise MultipleProfileVersionsError(profile_name)
        for path in to_remove:
            path.unlink()
        cls._remove_profile_directory(profile_name)

    @classmethod
    def list_stored_profile_names(cls) -> list[str]:
        """List all stored profile names sorted alphabetically including older storage versions."""
        filepaths = cls._get_storage_filepaths()
        profile_names = {key.name for key in filepaths}
        return sorted(profile_names)

    @classmethod
    def is_profile_stored(cls, profile_name: str) -> bool:
        return profile_name in cls.list_stored_profile_names()

    @classmethod
    def is_profile_filename(cls, file_name: str) -> bool:
        return file_name.endswith(cls.PROFILE_FILENAME_SUFFIX)

    @classmethod
    def get_profile_directory(cls, profile_name: str) -> Path:
        return cls._get_storage_directory() / profile_name

    @classmethod
    def get_current_version_profile_filename(cls) -> str:
        version_number = ProfileStorageBase.get_current_model_cls().get_this_version_number()
        return f"v{version_number}{cls.PROFILE_FILENAME_SUFFIX}"

    @classmethod
    def _get_storage_directory(cls) -> Path:
        return safe_settings.data_path / "data"

    @classmethod
    def _get_filepaths(cls, path_extension: str) -> ProfileNameModelToPath:
        storage_dir = cls._get_storage_directory()
        paths: PersistentStorageService.ProfileNameModelToPath = {}

        for path in storage_dir.glob(f"*/*{path_extension}"):
            if cls._is_valid_profile_filepath(path):
                name_model = cls.ProfileNameModel(
                    name=cls._profile_name_from_path(path),
                    model_cls=cls._model_cls_from_path(path),
                )
                paths[name_model] = path
        return paths

    @classmethod
    def _get_storage_filepaths(cls) -> ProfileNameModelToPath:
        return cls._get_filepaths(cls.PROFILE_FILENAME_SUFFIX)

    @classmethod
    def _get_backup_filepaths(cls) -> ProfileNameModelToPath:
        return cls._get_filepaths(cls.BACKUP_FILENAME_SUFFIX)

    @classmethod
    def _remove_profile_directory(cls, profile_name: str) -> None:
        profile_dir = cls.get_profile_directory(profile_name)
        if profile_dir.exists():
            profile_dir.rmdir()

    async def _save_profile_model(self, profile_model: ProfileStorageModel) -> None:
        """
        Save profile model to the storage.

        Args:
        ----
            profile_model: Profile model to be saved.

        Raises:
        ------
            ProfileEncryptionError: If profile could not be saved e.g. due to beekeeper wallet being locked
                or communication with beekeeper failed.
        """
        profile_directory = self.get_profile_directory(profile_model.name)

        # create data directory if it doesn't exist
        profile_directory.mkdir(parents=True, exist_ok=True)

        try:
            encrypted_profile = await self._encryption_service.encrypt(profile_model.json(indent=4))
        except (CommandEncryptError, CommandRequiresUnlockedEncryptionWalletError) as error:
            raise ProfileEncryptionError from error

        filepath = profile_directory / self.get_current_version_profile_filename()
        filepath.write_text(encrypted_profile)

    async def _find_or_migrate_profile_storage_model_by_name(self, profile_name: str) -> ProfileStorageModel:
        """
        Find current version of profile storage model by name in the clive data directory or migrate older version.

        Args:
        ----
            profile_name: Name of the profile to be found.

        Returns:
        -------
            ProfileStorageModel in current version if profile in current version exists,
            otherwise in older version that was most recently modified is taken and migrated to current version,
            this older version is then moved to backup.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be found.
            ProfileEncryptionError: If profile could not be loaded e.g. due to beekeeper wallet being locked
                or communication with beekeeper failed.
        """
        model_path = self._find_most_recent_profile_path(profile_name)

        if model_path is not None:
            encrypted_profile = model_path.read_text()

            try:
                decrypted_profile = await self._encryption_service.decrypt(encrypted_profile)
            except (CommandDecryptError, CommandRequiresUnlockedEncryptionWalletError) as error:
                raise ProfileEncryptionError from error

            model_cls = self._model_cls_from_path(model_path)
            model_instance = model_cls.parse_raw(decrypted_profile)
            model_migrated = apply_all_migrations(model_instance)
            if model_cls.get_this_version_number() != ProfileStorageBase.get_current_version_number():
                await self._save_profile_model(model_migrated)
                self._move_profile_to_backup(model_path)
            return model_migrated
        raise ProfileDoesNotExistsError(profile_name)

    @classmethod
    def _find_most_recent_profile_path(cls, profile_name: str) -> Path | None:
        filepaths = cls._get_storage_filepaths()
        keys = filter(lambda x: x.name == profile_name, filepaths.keys())
        if len(list(keys)) == 0:
            return None
        selected_key = max(keys, key=lambda x: x.version())
        return filepaths[selected_key]

    @classmethod
    def _move_profile_to_backup(cls, path: Path) -> None:
        backup_path = path.with_suffix(cls.BACKUP_FILENAME_SUFFIX)
        path.replace(backup_path)

    @classmethod
    def _raise_if_profile_not_stored(cls, profile_name: str) -> None:
        if not cls.is_profile_stored(profile_name):
            raise ProfileDoesNotExistsError(profile_name)

    def _raise_if_profile_with_name_already_exists_on_first_save(self, profile: Profile) -> None:
        profile_name = profile.name
        existing_profile_names = self.list_stored_profile_names()

        if profile.is_newly_created and profile_name in existing_profile_names:
            raise ProfileAlreadyExistsError(profile_name, existing_profile_names)

    @classmethod
    def _model_cls_from_path(cls, path: Path) -> type[ProfileStorageBase]:
        if path.parent.name == cls.FIRST_REVISION:
            return ProfileStorageBase.get_model_cls_for_version(0)

        pattern = r"^v(\d+)\.profile$"
        match_ = re.search(pattern, path.name)
        if not match_:
            raise ModelDoesNotExistsError(path)
        version_number = int(match_.group(1))
        if version_number >= len(ProfileStorageBase.REVISIONS):
            raise ModelDoesNotExistsError(path)
        return ProfileStorageBase.get_model_cls_for_version(version_number)

    @classmethod
    def _is_valid_profile_filepath(cls, path: Path) -> bool:
        try:
            cls._model_cls_from_path(path)
        except ModelDoesNotExistsError:
            return False
        else:
            return True

    @classmethod
    def _profile_name_from_path(cls, path: Path) -> str:
        profile_name_or_dir = path.parent.name
        if profile_name_or_dir == cls.FIRST_REVISION:
            return path.stem
        return profile_name_or_dir
