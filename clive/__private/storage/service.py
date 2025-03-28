from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final, Iterable, TypeAlias

from clive.__private.core.commands.abc.command_encryption import CommandRequiresUnlockedEncryptionWalletError
from clive.__private.core.commands.decrypt import CommandDecryptError
from clive.__private.core.commands.encrypt import CommandEncryptError
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.storage.model import (
    ProfileStorageModel,
    compare_versions,
    get_storage_version,
    get_storage_version_list,
    parse_and_upgrade_storage_model,
)
from clive.__private.storage.runtime_to_storage_converter import RuntimeToStorageConverter
from clive.__private.storage.storage_to_runtime_converter import StorageToRuntimeConverter
from clive.exceptions import CliveError

if TYPE_CHECKING:
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


class ProfileEncryptionError(PersistentStorageServiceError):
    """Raised when there is an issue with encryption or decryption of the profile e.g. during save or load."""

    MESSAGE: Final[str] = (
        "Profile encryption failed. Maybe the wallet is locked, or communication with the beekeeper failed?"
    )

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class PersistentStorageService:
    PROFILE_FILENAME_SUFFIX: Final[str] = ".profile"

    ProfileNameVersionToPath: TypeAlias = dict[tuple[str, str], Path]

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
        profile_hash = hash(profile)
        if profile.hash_of_stored_profile == profile_hash:
            logger.debug("Invoked save_profile but profile didn't change since last load/save.")
            return

        profile_name = profile.name
        profile_model = RuntimeToStorageConverter(profile).create_storage_model()

        await self._save_profile_model(profile_name, profile_model)
        profile._update_hash_of_stored_profile(profile_hash)

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
        profile_storage_model = await self._find_profile_storage_model_by_name(profile_name)

        profile = StorageToRuntimeConverter(profile_storage_model).create_profile()
        profile._update_hash_of_stored_profile()
        return profile

    @classmethod
    def delete_profile(cls, profile_name: str) -> None:
        """
        Remove profile with the given name from the storage, removes all storage versions.

        Args:
        ----
            profile_name: Name of the profile to be removed.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be removed.
        """
        cls._raise_if_profile_not_stored(profile_name)
        filepaths = cls._get_storage_filepaths()
        for (name, _version), path in filepaths.items():
            if name == profile_name:
                path.unlink()

    @classmethod
    def list_stored_profile_names(cls) -> list[str]:
        """List all stored profile names sorted alphabetically including older storage versions."""
        filepaths = cls._get_storage_filepaths()
        profile_names = {name for (name, _version), _path in filepaths.items()}
        return sorted(profile_names)

    @classmethod
    def is_profile_stored(cls, profile_name: str) -> bool:
        return profile_name in cls.list_stored_profile_names()

    @classmethod
    def is_profile_filename(cls, file_name: str) -> bool:
        return file_name.endswith(cls.PROFILE_FILENAME_SUFFIX)

    @classmethod
    def get_profile_filename(cls, profile_name: str) -> str:
        return f"{profile_name}{cls.PROFILE_FILENAME_SUFFIX}"

    @classmethod
    def _get_storage_directory(cls) -> Path:
        return safe_settings.data_path / "data"

    @classmethod
    def _get_storage_versioned_directory(cls) -> Path:
        """Get the directory where the current version of the storage file is stored."""
        return cls._get_storage_directory() / get_storage_version()

    @classmethod
    def _get_storage_filepaths(cls) -> ProfileNameVersionToPath:
        storage_dir = cls._get_storage_directory()
        allowed_versions = get_storage_version_list()
        paths = cls.ProfileNameVersionToPath()
        for profile_file_path in storage_dir.glob(f"*/*{cls.PROFILE_FILENAME_SUFFIX}"):
            path = Path(profile_file_path)
            profile_name = path.stem
            version = cls._calculate_version(path)
            if version in allowed_versions:
                paths[profile_name, version] = path
        return paths

    async def _save_profile_model(self, profile_name: str, profile_model: ProfileStorageModel) -> None:
        """
        Save profile model to the storage.

        Args:
        ----
            profile_name: Name of the profile to be saved.
            profile_model: Profile model to be saved.

        Raises:
        ------
            ProfileEncryptionError: If profile could not be saved e.g. due to beekeeper wallet being locked
                or communication with beekeeper failed.
        """
        versioned_storage_dir = PersistentStorageService._get_storage_versioned_directory()

        # create data directory if it doesn't exist
        versioned_storage_dir.mkdir(parents=True, exist_ok=True)

        try:
            encrypted_profile = await self._encryption_service.encrypt(profile_model.json(indent=4))
        except (CommandEncryptError, CommandRequiresUnlockedEncryptionWalletError) as error:
            raise ProfileEncryptionError from error

        filepath = versioned_storage_dir / self.get_profile_filename(profile_name)
        filepath.write_text(encrypted_profile)

    async def _find_profile_storage_model_by_name(self, profile_name: str) -> ProfileStorageModel:
        """
        Find latest version of profile storage model by name in the clive data directory.

        Args:
        ----
            profile_name: Name of the profile to be found.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be found.
            ProfileEncryptionError: If profile could not be loaded e.g. due to beekeeper wallet being locked
                or communication with beekeeper failed.
        """
        filepaths = self._get_storage_filepaths()
        selected_path: Path | None = None
        for (n, v), path in filepaths.items():
            if n == profile_name and (
                selected_path is None or compare_versions(v, self._calculate_version(selected_path)) > 0
            ):
                selected_path = path

        if selected_path is not None:
            encrypted_profile = selected_path.read_text()

            try:
                decrypted_profile = await self._encryption_service.decrypt(encrypted_profile)
            except (CommandDecryptError, CommandRequiresUnlockedEncryptionWalletError) as error:
                raise ProfileEncryptionError from error

            selected_version = self._calculate_version(selected_path)
            model = parse_and_upgrade_storage_model(decrypted_profile, selected_version)
            if selected_version != get_storage_version():
                await self._save_profile_model(profile_name, model)
            return model
        raise ProfileDoesNotExistsError(profile_name)

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
    def _calculate_version(cls, path: Path) -> str:
        return path.parent.name
