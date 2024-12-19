from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypeAlias

from clive.__private.core.commands.abc.command_encryption import CommandRequiresUnlockedEncryptionWalletError
from clive.__private.core.commands.decrypt import CommandDecryptError
from clive.__private.core.commands.encrypt import CommandEncryptError
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.storage.model import ProfileStorageModel, calculate_storage_model_revision
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

    ProfileNameToPath: TypeAlias = dict[str, Path]

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
        profile_storage_model = await self._find_profile_storage_model_by_name(profile_name)

        profile = StorageToRuntimeConverter(profile_storage_model).create_profile()
        profile._update_hash_of_stored_profile()
        return profile

    @classmethod
    def delete_profile(cls, profile_name: str) -> None:
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
        filepaths = cls._get_storage_filepaths()
        for name, path in filepaths.items():
            if name == profile_name:
                path.unlink()

    @classmethod
    def list_stored_profile_names(cls) -> list[str]:
        """List all stored profile names sorted alphabetically."""
        filepaths = cls._get_storage_filepaths()
        profile_names = filepaths.keys()
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
        """Get the directory where the storage file is stored in a versioned way."""
        revision = calculate_storage_model_revision()
        return cls._get_storage_directory() / revision

    @classmethod
    def _get_storage_filepaths(cls) -> ProfileNameToPath:
        versioned_storage_dir = cls._get_storage_versioned_directory()
        if not versioned_storage_dir.exists():
            return {}
        return {
            path.stem: path
            for path in versioned_storage_dir.iterdir()
            if path.is_file() and cls.is_profile_filename(path.name)
        }

    def _create_current_storage_symlink(self) -> None:
        versioned_storage_dir = self._get_storage_versioned_directory()
        symlink_dir = self._get_storage_directory() / "current"

        if symlink_dir.resolve() == versioned_storage_dir:
            logger.debug("Current storage symlink already points to the current version. Skipping symlink creation.")
            return

        symlink_dir.unlink(missing_ok=True)
        symlink_dir.symlink_to(versioned_storage_dir, target_is_directory=True)

    async def _save_profile_model(self, profile_model: ProfileStorageModel) -> None:
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
        self._create_current_storage_symlink()

        try:
            encrypted_profile = await self._encryption_service.encrypt(profile_model.json(indent=4))
        except (CommandEncryptError, CommandRequiresUnlockedEncryptionWalletError) as error:
            raise ProfileEncryptionError from error

        filepath = versioned_storage_dir / self.get_profile_filename(profile_model.name)
        filepath.write_text(encrypted_profile)

    async def _find_profile_storage_model_by_name(self, profile_name: str) -> ProfileStorageModel:
        """
        Find profile storage model by name in the given container of profiles.

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
        for name, path in filepaths.items():
            if name == profile_name:
                encrypted_profile = path.read_text()

                try:
                    decrypted_profile = await self._encryption_service.decrypt(encrypted_profile)
                except (CommandDecryptError, CommandRequiresUnlockedEncryptionWalletError) as error:
                    raise ProfileEncryptionError from error

                return ProfileStorageModel.parse_raw(decrypted_profile)
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
