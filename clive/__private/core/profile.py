from __future__ import annotations

from contextlib import asynccontextmanager
from copy import deepcopy
from typing import TYPE_CHECKING

from clive.__private.core.accounts.account_manager import AccountManager
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.keys import KeyManager, PublicKeyAliased
from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.storage.contextual import Context
from clive.__private.storage.service import PersistentStorageService, ProfileDoesNotExistsError
from clive.__private.validators.profile_name_validator import ProfileNameValidator
from clive.core.url import Url
from clive.exceptions import CliveError
from clive.models.aliased import ChainIdSchema, OperationBaseClass

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterable
    from types import TracebackType

    from typing_extensions import Self

    from clive.__private.core.accounts.accounts import KnownAccount, WatchedAccount, WorkingAccount


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


class Cart(list[OperationBaseClass]):
    def swap(self, index_1: int, index_2: int) -> None:
        self[index_1], self[index_2] = self[index_2], self[index_1]


class Profile(Context):
    def __init__(
        self,
        name: str,
        working_account: str | WorkingAccount | None = None,
        watched_accounts: Iterable[WatchedAccount] | None = None,
        known_accounts: Iterable[KnownAccount] | None = None,
    ) -> None:
        self.validate_profile_name(name)
        self.name = name
        self.cart = Cart()
        self.keys = KeyManager()

        self._accounts = AccountManager(working_account, watched_accounts, known_accounts)
        self._backup_node_addresses = self._default_node_address()
        self._set_node_address(self._initial_node_address())
        self._chain_id = self._default_chain_id()

        self._skip_save = False
        self._is_newly_created = True

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, __: BaseException | None, ___: TracebackType | None
    ) -> None:
        self.save()

    @property
    def is_newly_created(self) -> bool:
        """Determine if the profile is newly created (has not been saved yet)."""
        return self._is_newly_created

    def unset_is_newly_created(self) -> None:
        self._is_newly_created = False

    @property
    def accounts(self) -> AccountManager:
        return self._accounts

    @property
    def node_address(self) -> Url:
        return self._node_address

    @property
    def backup_node_addresses(self) -> list[Url]:
        return self._backup_node_addresses

    @property
    def chain_id(self) -> str | None:
        return self._chain_id

    def set_chain_id(self, value: str) -> None:
        if not is_schema_field_valid(ChainIdSchema, value):
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

    def save(self) -> None:
        """
        Save the current profile to the storage.

        Raises: # noqa: D406
        ------
            ProfileAlreadyExistsError: If profile is newly created and profile with that name already exists,
                it could not be saved, that would overwrite other profile.
        """
        if self._skip_save:
            return
        PersistentStorageService().save_profile(self)

    def delete(self) -> None:
        """
        Remove the current profile from the storage.

        Raises:  # noqa: D406
        ------
            ProfileDoesNotExistsError: If this profile is not stored, it could not be removed.
        """
        self.delete_by_name(self.name)

    @staticmethod
    def validate_profile_name(name: str) -> None:
        result = ProfileNameValidator().validate(name)
        if result.is_valid:
            return

        raise ProfileInvalidNameError(name, reason=humanize_validation_result(result))

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        name: str,
        working_account: str | WorkingAccount | None = None,
        watched_accounts: Iterable[WatchedAccount] | None = None,
        known_accounts: Iterable[KnownAccount] | None = None,
        key_aliases: Iterable[PublicKeyAliased] | None = None,
        cart_operations: Iterable[OperationBaseClass] | None = None,
        chain_id: str | None = None,
        node_address: str | Url | None = None,
        *,
        is_newly_created: bool = True,
    ) -> Profile:
        profile = cls(name, working_account, watched_accounts, known_accounts)
        profile.keys.add(*key_aliases or [])
        profile.cart.extend(cart_operations or [])
        if chain_id is not None:
            profile.set_chain_id(chain_id)
        if node_address is not None:
            secret_node_address = cls._get_secret_node_address()
            profile._set_node_address(secret_node_address or Url.parse(node_address))
        profile._is_newly_created = is_newly_created
        return profile

    @classmethod
    def list_profiles(cls) -> list[str]:
        """List all stored profile names sorted alphabetically."""
        return PersistentStorageService().list_stored_profile_names()

    @classmethod
    def is_default_profile_set(cls) -> bool:
        return PersistentStorageService().is_default_profile_set()

    @classmethod
    def get_default_profile_name(cls) -> str:
        """
        Get the profile name of default profile set in the storage.

        Args:
        ----
            storage: Storage model to be used. If not provided, storage will be loaded from the disk.

        Raises:
        ------
            NoDefaultProfileToLoadError: If no default profile is set, it could not be loaded.
        """
        return PersistentStorageService().get_default_profile_name()

    @classmethod
    def set_default_profile(cls, profile_name: str) -> None:
        """
        Set profile with the given name as default.

        Args:
        ----
            profile_name: Name of the profile to be set as default.

        Raises:
        ------
            ProfileDoesNotExistsError: If profile with given name does not exist, it could not be set as default.
        """
        PersistentStorageService().set_default_profile(profile_name)

    @classmethod
    def load(cls, name: str | None = None, *, auto_create: bool = True) -> Profile:
        """
        Load profile with the given name from the database.

        Cases:
        1. if name=None and is_default_profile_set=True -> load default profile
        2. if name=None and is_default_profile_set=False -> raise error
        3. if name="some_name" and is_default_profile_set=True -> load "some_name"
        4. if name="some_name" and is_default_profile_set=False -> load "some_name".

        Args:
        ----
            name: Name of the profile to load. If None, the default profile is loaded.
            auto_create: If True, a new profile is created if the profile with the given name does not exist.

        Raises:
        ------
            NoDefaultProfileToLoadError: If name is None but no default profile is set.
            ProfileDoesNotExistsError: If the profile does not exist and auto_create is False.
        """

        def create_new_profile(new_profile_name: str) -> Profile:
            return cls(new_profile_name)

        _name = name or cls.get_default_profile_name()

        try:
            return PersistentStorageService().load_profile(_name)
        except ProfileDoesNotExistsError:
            if auto_create:
                return create_new_profile(_name)
            raise

    @classmethod
    @asynccontextmanager
    async def load_with_auto_save(cls, name: str = "", *, auto_create: bool = True) -> AsyncIterator[Profile]:
        async with cls.load(name, auto_create=auto_create) as profile:
            yield profile

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
        PersistentStorageService().remove_profile(profile_name)

    def _initial_node_address(self) -> Url:
        secret_node_address = self._get_secret_node_address()
        if secret_node_address:
            return secret_node_address
        return self._backup_node_addresses[0]

    def _set_node_address(self, value: Url) -> None:
        """
        Set the node address.

        It is marked as not intended for usage because you rather should use Node.set_address instead.
        """
        self._node_address = value
        if value not in self._backup_node_addresses:
            # allow newly seen node address to be used as backup
            self._backup_node_addresses.insert(0, value)

    @staticmethod
    def _default_chain_id() -> str | None:
        return safe_settings.node.chain_id

    @staticmethod
    def _default_node_address() -> list[Url]:
        return [
            Url("https", "api.hive.blog"),
            Url("https", "api.openhive.network"),
        ]

    @staticmethod
    def _get_secret_node_address() -> Url | None:
        return safe_settings.secrets.node_address
