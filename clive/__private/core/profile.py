from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Final

from beekeepy.interfaces import HttpUrl

from clive.__private.core.accounts.account_manager import AccountManager
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.keys import KeyManager, PublicKeyAliased
from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.logger import logger
from clive.__private.models import Transaction
from clive.__private.models.schemas import ChainId, OperationRepresentationUnion, OperationUnion
from clive.__private.settings import safe_settings
from clive.__private.storage.runtime_to_storage_converter import RuntimeToStorageConverter
from clive.__private.storage.service import PersistentStorageService
from clive.__private.validators.profile_name_validator import ProfileNameValidator
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from typing_extensions import Self

    from clive.__private.core.accounts.accounts import Account
    from clive.__private.core.encryption import EncryptionService


class ProfileError(CliveError):
    """An error related to profile."""


class InvalidChainIdError(ProfileError):
    """Raised when an invalid chain id is set."""

    def __init__(self) -> None:
        super().__init__("Invalid chain ID. Should be a 64 character long hex string.")


class ProfileInvalidNameError(ProfileError):
    def __init__(self, profile_name: str, reason: str | None = None) -> None:
        self.profile_name = profile_name
        self.reason = reason
        message = f"Profile name `{profile_name}` is invalid."
        message += f" Reason: {reason}" if reason else ""
        super().__init__(message)


class Profile:
    _INIT_KEY: Final[object] = object()
    """Used to prevent direct initialization of the class. Instead factory methods should be used."""

    def __init__(  # noqa: PLR0913
        self,
        init_key: object,
        name: str,
        working_account: str | Account | None = None,
        watched_accounts: Iterable[str | Account] | None = None,
        known_accounts: Iterable[str | Account] | None = None,
        key_aliases: Iterable[PublicKeyAliased] | None = None,
        transaction: Transaction | None = None,
        transaction_file_path: Path | None = None,
        chain_id: str | None = None,
        node_address: str | HttpUrl | None = None,
        *,
        should_enable_known_accounts: bool = True,
    ) -> None:
        self._assert_no_direct_initialization(init_key)

        self.name = name
        self.keys = KeyManager()
        self.keys.add(*key_aliases or [])
        self.transaction = transaction if transaction else Transaction()
        self.transaction_file_path = transaction_file_path if transaction_file_path else None

        self._accounts = AccountManager(working_account, watched_accounts, known_accounts)

        self._backup_node_addresses = self._default_node_addresses()
        self._node_address: HttpUrl | None = None
        self._set_node_address(self._get_initial_node_address(node_address))

        self._chain_id: str | None = None
        self.set_chain_id(chain_id or self._default_chain_id())

        self._skip_save = False
        self._hash_of_stored_profile: int | None = None
        self._should_enable_known_accounts = should_enable_known_accounts

    def __hash__(self) -> int:
        return hash(RuntimeToStorageConverter(self).create_storage_model())

    @property
    def hash_of_stored_profile(self) -> int | None:
        """Return hash of stored profile, None if profile is not stored."""
        return self._hash_of_stored_profile

    @property
    def is_newly_created(self) -> bool:
        """Determine if the profile is newly created (has not been saved yet)."""
        return self._hash_of_stored_profile is None

    @property
    def accounts(self) -> AccountManager:
        return self._accounts

    @property
    def node_address(self) -> HttpUrl:
        assert self._node_address is not None, "Node address is not set."
        return self._node_address

    @property
    def backup_node_addresses(self) -> list[HttpUrl]:
        return self._backup_node_addresses

    @property
    def chain_id(self) -> str | None:
        return self._chain_id

    @property
    def operations(self) -> list[OperationUnion]:
        return self.transaction.operations_models

    @property
    def operation_representations(self) -> list[OperationRepresentationUnion]:
        return self.transaction.operations

    @property
    def is_skip_save_set(self) -> bool:
        return self._skip_save

    @property
    def should_be_saved(self) -> bool:
        return not self.is_skip_save_set and self.hash_of_stored_profile != hash(self)

    @property
    def should_enable_known_accounts(self) -> bool:
        return self._should_enable_known_accounts

    def add_operation(self, *operations: OperationUnion) -> None:
        self.transaction.add_operation(*operations)

    def remove_operation(self, *operations: OperationUnion) -> None:
        self.transaction.remove_operation(*operations)

    def set_chain_id(self, value: str | None) -> None:
        """
        Set the chain id.

        Args:
        ----
            value: Chain id to be set. If None, it will be fetched from the node api.
        """
        if not is_schema_field_valid(ChainId, value):
            raise InvalidChainIdError

        self._chain_id = value

    def unset_chain_id(self) -> None:
        """When no chain_id is set, it should be fetched from the node api."""
        self._chain_id = None

    def skip_saving(self) -> None:
        logger.debug(f"Skipping saving of profile: {self.name} with id {id(self)}")
        self._skip_save = True

    def enable_saving(self) -> None:
        logger.debug(f"Enabling saving of profile: {self.name} with id {id(self)}")
        self._skip_save = False

    def copy(self) -> Self:
        return deepcopy(self)

    def enable_known_accounts(self) -> None:
        self._should_enable_known_accounts = True

    def disable_known_accounts(self) -> None:
        self._should_enable_known_accounts = False

    async def save(self, encryption_service: EncryptionService) -> None:
        """
        Save the current profile to the storage.

        Args:
        ----
            encryption_service: Service for encrypting and decrypting data.

        Raises:
        ------
            ProfileAlreadyExistsError: If profile is newly created and profile with that name already exists,
                it could not be saved, that would overwrite other profile.
            ProfileEncryptionError: If profile could not be saved e.g. due to beekeeper wallet being locked
                or communication with beekeeper failed.
        """
        await PersistentStorageService(encryption_service).save_profile(self)

    def delete(self) -> None:
        """
        Remove the current profile from the storage.

        Raises:  # noqa: D406
        ------
            ProfileDoesNotExistsError: If this profile is not stored, it could not be removed.
        """
        self._unset_hash_of_stored_profile()
        self.delete_by_name(self.name)

    @classmethod
    def is_any_profile_saved(cls) -> bool:
        return bool(cls.list_profiles())

    @classmethod
    def is_only_one_profile_saved(cls) -> bool:
        return len(cls.list_profiles()) == 1

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        name: str,
        working_account: str | Account | None = None,
        watched_accounts: Iterable[str | Account] | None = None,
        known_accounts: Iterable[str | Account] | None = None,
        key_aliases: Iterable[PublicKeyAliased] | None = None,
        transaction: Transaction | None = None,
        transaction_file_path: Path | None = None,
        chain_id: str | None = None,
        node_address: str | HttpUrl | None = None,
        *,
        should_enable_known_accounts: bool = True,
    ) -> Profile:
        cls.validate_profile_name(name)
        return cls._create_instance(
            name,
            working_account,
            watched_accounts,
            known_accounts,
            key_aliases,
            transaction,
            transaction_file_path,
            chain_id,
            node_address,
            should_enable_known_accounts=should_enable_known_accounts,
        )

    @classmethod
    def list_profiles(cls) -> list[str]:
        """List all stored profile names sorted alphabetically."""
        return PersistentStorageService.list_stored_profile_names()

    @classmethod
    async def load(cls, name: str, encryption_service: EncryptionService) -> Profile:
        """
        Load profile with the given name from the database.

        Args:
        ----
            name: Name of the profile to load.
            encryption_service: Service for encrypting and decrypting data.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be loaded
            ProfileEncryptionError: If profile could not be loaded e.g. due to beekeeper wallet being locked
                or communication with beekeeper failed.
        """
        return await PersistentStorageService(encryption_service).load_profile(name)

    @classmethod
    def delete_by_name(cls, profile_name: str) -> None:
        """
        Remove profile with the given name from the storage.

        Args:
        ----
            profile_name: Name of the profile to be removed.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be removed.
        """
        PersistentStorageService.delete_profile(profile_name)

    @classmethod
    def _create_instance(  # noqa: PLR0913
        cls,
        name: str,
        working_account: str | Account | None = None,
        watched_accounts: Iterable[str | Account] | None = None,
        known_accounts: Iterable[str | Account] | None = None,
        key_aliases: Iterable[PublicKeyAliased] | None = None,
        transaction: Transaction | None = None,
        transaction_file_path: Path | None = None,
        chain_id: str | None = None,
        node_address: str | HttpUrl | None = None,
        *,
        should_enable_known_accounts: bool = True,
    ) -> Self:
        """Create new instance bypassing blocked direct initializer call."""
        return cls(
            cls._INIT_KEY,
            name,
            working_account,
            watched_accounts,
            known_accounts,
            key_aliases,
            transaction,
            transaction_file_path,
            chain_id,
            node_address,
            should_enable_known_accounts=should_enable_known_accounts,
        )

    @staticmethod
    def validate_profile_name(name: str) -> None:
        result = ProfileNameValidator().validate(name)
        if result.is_valid:
            return

        raise ProfileInvalidNameError(name, reason=humanize_validation_result(result))

    @staticmethod
    def _default_chain_id() -> str | None:
        return safe_settings.node.chain_id

    @staticmethod
    def _default_node_addresses() -> list[HttpUrl]:
        return [
            HttpUrl("api.hive.blog", protocol="https"),
            HttpUrl("api.openhive.network", protocol="https"),
        ]

    @staticmethod
    def _get_secret_node_address() -> HttpUrl | None:
        return safe_settings.secrets.node_address

    def _update_hash_of_stored_profile(self, new_hash: int | None = None) -> None:
        """Update the hash of stored profile to a given value. None means recalculate."""
        self._hash_of_stored_profile = new_hash if new_hash is not None else hash(self)

    def _unset_hash_of_stored_profile(self) -> None:
        self._hash_of_stored_profile = None

    def _get_initial_node_address(self, given_node_address: str | HttpUrl | None = None) -> HttpUrl:
        secret_node_address = self._get_secret_node_address()
        if secret_node_address:
            return secret_node_address
        if given_node_address:
            return HttpUrl(given_node_address)
        return self._backup_node_addresses[0]

    def _set_node_address(self, value: HttpUrl) -> None:
        """
        Set the node address.

        It is marked as not intended for usage because you rather should use Node.set_address instead.
        """
        self._node_address = value
        if value not in self._backup_node_addresses:
            # allow newly seen node address to be used as backup
            self._backup_node_addresses.insert(0, value)

    def _assert_no_direct_initialization(self, init_key: object) -> None:
        message = f"Please use {self.create} to create a new profile or {self.load} to load an existing one."
        assert init_key is self._INIT_KEY, message
