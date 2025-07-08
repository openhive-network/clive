from __future__ import annotations

import contextlib
import re
import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal

from clive.__private.core.commands.abc.command_encryption import CommandRequiresUnlockedEncryptionWalletError
from clive.__private.core.commands.decrypt import CommandDecryptError
from clive.__private.core.commands.encrypt import CommandEncryptError
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.storage.runtime_to_storage_converter import RuntimeToStorageConverter
from clive.__private.storage.storage_history import StorageHistory
from clive.__private.storage.storage_to_runtime_converter import StorageToRuntimeConverter
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from pathlib import Path

    from clive.__private.core.encryption import EncryptionService
    from clive.__private.core.profile import Profile
    from clive.__private.core.types import MigrationStatus
    from clive.__private.storage import ProfileStorageBase, ProfileStorageModel


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
    """Raised when there is an issue with encryption or decryption of the profile e.g. during save or load."""

    MESSAGE: Final[str] = (
        "Profile encryption failed. Maybe the wallet is locked, or communication with the beekeeper failed?"
    )

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


@dataclass
class _MigrationResult:
    model: ProfileStorageModel
    status: MigrationStatus


class PersistentStorageService:
    BACKUP_FILENAME_SUFFIX: Final[str] = ".backup"
    PROFILE_FILENAME_SUFFIX: Final[str] = ".profile"
    PROFILE_VERSION_FILE_REGEX: Final[str] = r"^v(\d+)\.(profile|backup)$"
    FIRST_REVISION: Final[str] = "c600278a"

    ProfileFileTypes = Literal["profile", "backup", "all"]

    @dataclass(frozen=True)
    class ProfileFileInfo:
        profile_name: str
        path: Path
        model_cls: type[ProfileStorageBase] | None = None

        @property
        def is_backup(self) -> bool:
            return self.path.suffix == PersistentStorageService.BACKUP_FILENAME_SUFFIX

        def version(self) -> int:
            assert self.model_cls is not None, "Could not determine version because model is not available."
            return self.model_cls.get_this_version()

    def __init__(self, encryption_service: EncryptionService) -> None:
        self._encryption_service = encryption_service

    async def save_profile(self, profile: Profile) -> None:
        """
        Save profile to the storage.

        Args:
            profile: Profile to be saved.

        Raises:
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
            profile_name: Name of the profile to be loaded.

        Raises:
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be loaded
            ProfileEncryptionError: If profile could not be loaded e.g. due to beekeeper wallet being locked
                or communication with beekeeper failed.

        Returns:
            Loaded profile object.
        """
        self._raise_if_profile_not_stored(profile_name)
        result = await self._load_and_migrate_latest_profile_model(profile_name)
        profile_storage_model = result.model

        profile = StorageToRuntimeConverter(profile_storage_model).create_profile()
        profile._update_hash_of_stored_profile()
        return profile

    async def migrate(self, profile_name: str) -> MigrationStatus:
        result = await self._load_and_migrate_latest_profile_model(profile_name)
        return result.status

    @classmethod
    def delete_profile(cls, profile_name: str, *, force: bool = False) -> None:
        """
        Remove profile with the given name from the storage.

        Args:
            profile_name: Name of the profile to be removed, removes all storage versions.
            force: If True, remove all profile versions, also not migrated/backed-up.
                If False and multiple versions exist, raise error.

        Raises:
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be removed.
            MultipleProfileVersionsError: If multiple versions / back-ups of profile exist and force is False.
        """
        filepaths = cls._get_filepaths(profile_name, file_type="all", include_impossible_to_load=True)
        only_backups_found = filepaths and all(filepath.is_backup for filepath in filepaths)
        num_of_files_to_remove = len(filepaths)

        if num_of_files_to_remove == 0:
            raise ProfileDoesNotExistsError(profile_name)
        if not force:
            if only_backups_found:
                raise ProfileDoesNotExistsError(profile_name)
            if num_of_files_to_remove > 1:
                raise MultipleProfileVersionsError(profile_name)

        cls._delete_legacy_profile_data(profile_name)
        profile_dir = cls.get_profile_directory(profile_name)
        if profile_dir.exists():  # we can store only a legacy version of the profile
            shutil.rmtree(profile_dir)

    @classmethod
    def list_stored_profile_names(cls) -> list[str]:
        """List all stored profile names sorted alphabetically including older storage versions."""
        profile_names = {filepath.profile_name for filepath in cls._get_filepaths()}
        return sorted(profile_names)

    @classmethod
    def is_profile_stored(cls, profile_name: str) -> bool:
        return profile_name in cls.list_stored_profile_names()

    @classmethod
    def is_profile_file(cls, path: Path, *, file_type: ProfileFileTypes = "profile") -> bool:
        conditions: list[Callable[[], bool]] = [
            lambda: path.is_file(),
            lambda: path.suffix in cls._get_suffixes_for_file_type(file_type),
            lambda: cls.get_version_from_profile_file(path) is not None,
        ]
        if path.parent.name == cls.FIRST_REVISION:
            # in the legacy structure, there was no version in the filename
            return all(condition() for condition in conditions[:2])
        return all(condition() for condition in conditions)

    @classmethod
    def get_profile_directory(cls, profile_name: str) -> Path:
        return cls._get_storage_directory() / profile_name

    @classmethod
    def get_version_profile_filename(cls, version: int) -> str:
        return f"v{version}{cls.PROFILE_FILENAME_SUFFIX}"

    @classmethod
    def get_current_version_profile_filename(cls) -> str:
        return cls.get_version_profile_filename(StorageHistory.get_latest_version())

    @classmethod
    def get_version_from_profile_file(cls, filepath: Path) -> int | None:
        match = re.match(cls.PROFILE_VERSION_FILE_REGEX, filepath.name)
        return int(match.group(1)) if match else None

    @classmethod
    def _get_suffixes_for_file_type(cls, file_type: ProfileFileTypes) -> list[str]:
        if file_type == "profile":
            return [cls.PROFILE_FILENAME_SUFFIX]
        if file_type == "backup":
            return [cls.BACKUP_FILENAME_SUFFIX]
        return [cls.PROFILE_FILENAME_SUFFIX, cls.BACKUP_FILENAME_SUFFIX]

    @classmethod
    def _delete_legacy_profile_data(cls, profile_name: str) -> None:
        cls._get_legacy_profile_filepath(profile_name).unlink(missing_ok=True)
        cls._get_legacy_backup_filepath(profile_name).unlink(missing_ok=True)
        with contextlib.suppress(OSError):
            # remove the directory only if empty
            cls._get_legacy_profile_directory().rmdir()

    @classmethod
    def _get_legacy_profile_directory(cls) -> Path:
        return cls._get_storage_directory() / cls.FIRST_REVISION

    @classmethod
    def _get_legacy_profile_filepath(cls, profile_name: str) -> Path:
        return cls._get_legacy_profile_directory() / f"{profile_name}{cls.PROFILE_FILENAME_SUFFIX}"

    @classmethod
    def _get_legacy_backup_filepath(cls, profile_name: str) -> Path:
        return cls._get_legacy_profile_directory() / f"{profile_name}{cls.BACKUP_FILENAME_SUFFIX}"

    @classmethod
    def _get_storage_directory(cls) -> Path:
        return safe_settings.data_path / "data"

    @classmethod
    def _get_profile_filepath_to_read(cls, profile_name: str) -> Path | None:
        filepaths = cls._get_filepaths(profile_name)
        if not filepaths:
            return None

        # Pick the path with the highest version
        highest_version = max(filepaths, key=lambda item: item.version())
        return highest_version.path

    @classmethod
    def _get_filepaths(
        cls,
        profile_name: str | None = None,
        file_type: ProfileFileTypes = "profile",
        *,
        include_impossible_to_load: bool = False,
    ) -> set[PersistentStorageService.ProfileFileInfo]:
        """
        Retrieve file paths of profiles stored on the disk.

        If include_impossible_to_load=False, it will retrieve only profiles that
        we have a corresponding version of model for.
        It means any newer versions won't be picked up. (Like we're on v2, but there is v3.profile)

        Args:
            profile_name: If given, only profiles with this name will be returned. If None, return all profiles.
            file_type: Determine which type of files to look for.
            include_impossible_to_load: If True, it will return profiles even we could not load them.

        Returns:
            A set of objects containing information about the stored profiles.
        """
        storage_dir = cls._get_storage_directory()
        paths: set[PersistentStorageService.ProfileFileInfo] = set()

        for path in storage_dir.glob("*/*"):
            if not cls.is_profile_file(path, file_type=file_type):
                continue

            is_model_cls_available = cls._is_model_cls_for_versioned_profile_file_available(path)
            if not include_impossible_to_load and not is_model_cls_available:
                continue

            profile_name_from_path = cls._profile_name_from_path(path)
            if profile_name is not None and profile_name != profile_name_from_path:
                continue

            name_model = cls.ProfileFileInfo(
                profile_name=profile_name_from_path,
                model_cls=cls._model_cls_from_path(path) if is_model_cls_available else None,
                path=path,
            )
            paths.add(name_model)
        return paths

    async def _save_profile_model(self, profile_model: ProfileStorageModel) -> None:
        """
        Save profile model to the storage.

        Args:
            profile_model: Profile model to be saved.

        Raises:
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

    async def _load_and_migrate_latest_profile_model(self, profile_name: str) -> _MigrationResult:
        """
        Find current version of profile storage model by name in the clive data directory or migrate older version.

        Args:
            profile_name: Name of the profile to be found.

        Returns:
            ProfileStorageModel in current version if profile in current version exists,
            otherwise in older version that was most recently modified is taken and migrated to current version,
            this older version is then moved to backup.

        Raises:
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be found.
        """
        profile_filepath = self._get_profile_filepath_to_read(profile_name)
        if profile_filepath is None:
            raise ProfileDoesNotExistsError(profile_name)

        profile_model = await self._parse_profile_model_from_file(profile_filepath)
        return await self._migrate_profile_model(profile_model, profile_filepath)

    async def _parse_profile_model_from_file(self, profile_filepath: Path) -> ProfileStorageBase:
        raw = await self._read_profile_file_raw(profile_filepath)
        model_cls = self._model_cls_from_path(profile_filepath)
        return model_cls.parse_raw(raw)

    async def _read_profile_file_raw(self, profile_filepath: Path) -> str:
        encrypted_profile = profile_filepath.read_text()
        try:
            decrypted_profile = await self._encryption_service.decrypt(encrypted_profile)
        except (CommandDecryptError, CommandRequiresUnlockedEncryptionWalletError) as error:
            raise ProfileEncryptionError from error
        return decrypted_profile

    async def _migrate_profile_model(
        self, profile_model: ProfileStorageBase, profile_filepath: Path
    ) -> _MigrationResult:
        """Migrate profile model and return current version of model even it there was no migration needed."""
        was_migrated = False
        model_migrated = StorageHistory.apply_all_migrations(profile_model)
        if profile_model.get_this_version() != StorageHistory.get_latest_version():
            await self._save_profile_model(model_migrated)
            self._move_profile_to_backup(profile_filepath)
            was_migrated = True
        return _MigrationResult(model_migrated, status="migrated" if was_migrated else "already_newest")

    @classmethod
    def _move_profile_to_backup(cls, path: Path) -> None:
        cls._assert_path_is_profile_file(path)

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
        cls._assert_path_is_profile_file(path, file_type="all")

        if path.parent.name == cls.FIRST_REVISION:
            return StorageHistory.get_model_cls_for_version(0)

        version = cls.get_version_from_profile_file(path)

        if version not in StorageHistory.get_versions():
            raise ModelDoesNotExistsError(path)
        return StorageHistory.get_model_cls_for_version(version)

    @classmethod
    def _is_model_cls_for_versioned_profile_file_available(cls, path: Path) -> bool:
        """Determine if we have a corresponding version of model for the given path."""
        try:
            cls._model_cls_from_path(path)
        except ModelDoesNotExistsError:
            return False
        else:
            return True

    @classmethod
    def _profile_name_from_path(cls, path: Path) -> str:
        cls._assert_path_is_profile_file(path, file_type="all")

        profile_name_or_dir = path.parent.name
        if profile_name_or_dir == cls.FIRST_REVISION:
            # previously profile name was in the file name
            return path.stem
        # now directory name is the profile name
        return profile_name_or_dir

    @classmethod
    def _assert_path_is_profile_file(cls, path: Path, *, file_type: ProfileFileTypes = "profile") -> None:
        assert cls.is_profile_file(path, file_type=file_type), f"Looks like {path} is not a profile file."
