from __future__ import annotations

import shelve
from contextlib import asynccontextmanager, contextmanager
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from clive.__private.core.clive_import import get_clive
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.keys import KeyManager
from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.storage.accounts import Account, WorkingAccount
from clive.__private.storage.contextual import Context
from clive.__private.validators.profile_name_validator import ProfileNameValidator
from clive.core.url import Url
from clive.exceptions import CliveError
from clive.models import Operation
from clive.models.aliased import ChainIdSchema

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterable, Iterator
    from types import TracebackType

    from typing_extensions import Self


class ProfileDataError(CliveError):
    """An error related to profile data."""


class InvalidChainIdError(ProfileDataError):
    """Raised when an invalid chain id is set."""

    def __init__(self) -> None:
        super().__init__("Invalid chain ID. Should be a 64 character long hex string.")


class NoWorkingAccountError(ProfileDataError):
    """No working account is available."""


class WatchedAccountNotFoundError(ProfileDataError):
    """Raised when an account is not found in `get_watched_account` method."""

    def __init__(self, account_name: str) -> None:
        super().__init__(f"Account {account_name} not found in watched accounts")
        self.account_name = account_name


class AccountNotFoundError(ProfileDataError):
    """Raised when an account is not found in `get_account_by_name` method."""

    def __init__(self, account_name: str) -> None:
        super().__init__(f"Account {account_name} not found in tracked accounts (working + watched accounts)")
        self.account_name = account_name


class ProfileCouldNotBeLoadedError(ProfileDataError):
    """Raised when a profile could not be loaded."""


class ProfileCouldNotBeDeletedError(ProfileDataError):
    """Raised when a profile could not be deleted."""


class ProfileDoesNotExistsError(ProfileCouldNotBeLoadedError, ProfileCouldNotBeDeletedError):
    def __init__(self, profile_name: str) -> None:
        self.profile_name = profile_name
        super().__init__(f"Profile `{profile_name}` does not exist.")


class NoDefaultProfileToLoadError(ProfileCouldNotBeLoadedError):
    """Raised when default profile is not set."""


class ProfileSaveError(ProfileDataError):
    """Raised when a profile could not be saved."""


class ProfileAlreadyExistsError(ProfileDataError):
    def __init__(self, profile_name: str, existing_profiles: list[str] | None = None) -> None:
        self.profile_name = profile_name
        self.existing_profiles = existing_profiles
        detail = f", different than {existing_profiles}." if existing_profiles else "."
        message = f"Profile `{self.profile_name}` already exists. Please choose another name{detail}"
        super().__init__(message)


class ProfileInvalidNameError(ProfileDataError):
    def __init__(self, profile_name: str, reason: str | None = None) -> None:
        self.profile_name = profile_name
        self.reason = reason
        message = f"Profile name `{profile_name}` is invalid."
        message += f" Reason: {reason}" if reason else ""
        super().__init__(message)


class Cart(list[Operation]):
    def swap(self, index_1: int, index_2: int) -> None:
        self[index_1], self[index_2] = self[index_2], self[index_1]


class ProfileData(Context):
    ONBOARDING_PROFILE_NAME: Final[str] = "onboarding"
    _DEFAULT_PROFILE_IDENTIFIER: Final[str] = "!default_profile"

    def __init__(
        self,
        name: str,
        working_account: str | WorkingAccount | None = None,
        watched_accounts: Iterable[Account] | None = None,
        known_accounts: Iterable[Account] | None = None,
    ) -> None:
        self.validate_profile_name(name)

        self.name = name
        self.__working_account: WorkingAccount | None = None
        self.watched_accounts = set(watched_accounts or [])
        self.known_accounts = set(known_accounts or [])

        if working_account is not None:
            self.set_working_account(working_account)

        self.__chain_id = self.__default_chain_id()

        self.cart = Cart()
        self.keys = KeyManager()

        if address := self.__get_secret_node_address():
            self.__backup_node_addresses = [address]
            self.__node_address = address
        else:
            self.__backup_node_addresses = self.__default_node_address()
            self.__node_address = self.__backup_node_addresses[0]

        self.__first_time_save = True
        self.__skip_save = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, __: BaseException | None, ___: TracebackType | None
    ) -> None:
        self.save()

    def copy(self) -> Self:
        return deepcopy(self)

    @staticmethod
    def validate_profile_name(name: str) -> None:
        result = ProfileNameValidator().validate(name)
        if result.is_valid:
            return

        raise ProfileInvalidNameError(name, reason=humanize_validation_result(result))

    def get_account_by_name(self, value: str | Account) -> Account:
        searched_account_name = self._get_account_name(value)
        for account in self.get_tracked_accounts():
            if account.name == searched_account_name:
                return account

        raise AccountNotFoundError(searched_account_name)

    @property
    def working_account(self) -> WorkingAccount:
        """
        Returns the working account.

        Raises
        ------
        NoWorkingAccountError: If no working account is set.
        """
        if not self.is_working_account_set():
            raise NoWorkingAccountError
        assert self.__working_account is not None
        return self.__working_account

    @property
    def watched_accounts_sorted(self) -> list[Account]:
        return sorted(self.watched_accounts, key=lambda account: account.name)

    @property
    def known_accounts_sorted(self) -> list[Account]:
        return sorted(self.known_accounts, key=lambda account: account.name)

    @property
    def tracked_accounts_sorted(self) -> list[Account]:
        """Working account is always first then watched accounts sorted alphabetically."""
        return sorted(
            self.get_tracked_accounts(),
            key=lambda account: (not isinstance(account, WorkingAccount), account.name),
        )

    @staticmethod
    def _get_account_name(account: str | Account) -> str:
        return account if isinstance(account, str) else account.name

    def set_working_account(self, value: str | WorkingAccount) -> None:
        if isinstance(value, str):
            value = WorkingAccount(value)
        self.__working_account = value

    def switch_working_account(self, new_working_account: str | Account | None = None) -> None:
        """
        Switch the working account to the one of watched accounts and move the old one to the watched accounts.

        Working account can be deleted and moved to watched accounts if `new_working_account` is None.
        """

        def is_given_account_already_working() -> bool:
            return new_working_account is not None and self.is_account_working(new_working_account)

        if is_given_account_already_working():
            return

        if self.is_working_account_set():
            # we allow for switching from no working account to watched account
            self.move_working_account_to_watched()

        if new_working_account is not None:
            # we allow for only moving the current working account to watched accounts
            self.set_watched_account_as_working(new_working_account)

    def is_account_working(self, account: Account | str) -> bool:
        if not self.is_working_account_set():
            return False

        account_name = self._get_account_name(account)
        return self.working_account.name == account_name

    def move_working_account_to_watched(self) -> None:
        name, data, alarms = self.working_account.name, self.working_account._data, self.working_account._alarms

        new_account_object = Account(name, alarms)
        new_account_object._data = data

        self.unset_working_account()
        self.watched_accounts.add(new_account_object)

    def set_watched_account_as_working(self, account: Account | str) -> None:
        account = self.get_watched_account(account)

        self.remove_watched_account(account)
        new_working_account = WorkingAccount(account.name, account._alarms)
        new_working_account._data = account._data

        self.set_working_account(new_working_account)

    def unset_working_account(self) -> None:
        self.__working_account = None

    @property
    def node_address(self) -> Url:
        return self.__get_secret_node_address() or self.__node_address

    @property
    def backup_node_addresses(self) -> list[Url]:
        if secret_node_address := self.__get_secret_node_address():
            return [secret_node_address]
        return self.__backup_node_addresses

    def _set_node_address(self, value: Url) -> None:
        """
        Set the node address.

        It is marked as not intended for usage because you rather should use Node.set_address instead.
        """
        self.__node_address = value

    @property
    def chain_id(self) -> str | None:
        return self.__chain_id

    def set_chain_id(self, value: str) -> None:
        if not is_schema_field_valid(ChainIdSchema, value):
            raise InvalidChainIdError

        self.__chain_id = value

    def unset_chain_id(self) -> None:
        """When no chain_id is set, it should be fetched from the node api."""
        self.__chain_id = None

    def is_working_account_set(self) -> bool:
        return self.__working_account is not None

    def is_account_tracked(self, account: str | Account) -> bool:
        account_name = self._get_account_name(account)
        return account_name not in [tracked_account.name for tracked_account in self.get_tracked_accounts()]

    def get_tracked_accounts(self) -> set[Account]:
        accounts = self.watched_accounts.copy()
        if self.is_working_account_set():
            accounts.add(self.working_account)
        return accounts

    def get_watched_account(self, account: str | Account) -> Account:
        account_to_find: Account = self.get_account_by_name(account) if isinstance(account, str) else account

        if account_to_find in self.watched_accounts:
            return account_to_find

        raise WatchedAccountNotFoundError(account_to_find.name)

    def has_known_accounts(self) -> bool:
        return bool(self.known_accounts)

    def has_tracked_accounts(self) -> bool:
        return bool(self.get_tracked_accounts())

    def remove_tracked_account(self, to_remove: str | Account) -> None:
        account_name = self._get_account_name(to_remove)
        if self.is_working_account_set() and account_name == self.working_account.name:
            self.unset_working_account()
        else:
            self.remove_watched_account(to_remove)

    def remove_watched_account(self, to_remove: str | Account) -> None:
        account_name = self._get_account_name(to_remove)
        account = next((account for account in self.watched_accounts if account.name == account_name), None)
        if account is not None:
            self.watched_accounts.discard(account)

    @property
    def is_accounts_alarms_data_available(self) -> bool:
        tracked_accounts = self.get_tracked_accounts()
        if not tracked_accounts:
            return False

        return all(account.is_alarms_data_available for account in tracked_accounts)

    @property
    def is_accounts_node_data_available(self) -> bool:
        tracked_accounts = self.get_tracked_accounts()
        if not tracked_accounts:
            return False

        return all(account.is_node_data_available for account in tracked_accounts)

    @classmethod
    def _get_file_storage_path(cls) -> Path:
        return Path(safe_settings.data_path) / "data/profile"

    def save(self) -> None:
        if self.__skip_save:
            return

        existing_profiles = self.list_profiles()
        if self.__first_time_save and self.name in existing_profiles:
            raise ProfileAlreadyExistsError(self.name, existing_profiles)
        self.__first_time_save = False

        clive = get_clive().app_instance()

        if clive.is_launched:
            clive.trigger_profile_data_watchers()

        with self.__open_database() as db:
            db[self.name] = self._prepare_for_save()

        # set the profile as default if that's not already set (first profile is set always as default)
        if not self.is_default_profile_set():
            self.set_default_profile(self.name)

    def _prepare_for_save(self) -> Self:
        this = deepcopy(self)
        for account in this.get_tracked_accounts():
            account._prepare_for_save()
        return this

    @classmethod
    def set_default_profile(cls, name: str) -> None:
        if name not in cls.list_profiles():
            raise ProfileDoesNotExistsError(name)

        with cls.__open_database() as db:
            db[cls._DEFAULT_PROFILE_IDENTIFIER] = name

    def skip_saving(self) -> None:
        self.__skip_save = True

    def delete(self) -> None:
        self.delete_by_name(self.name)

    @classmethod
    def delete_by_name(cls, name: str) -> None:
        with cls.__open_database() as db:
            try:
                del db[name]
            except KeyError as error:
                raise ProfileDoesNotExistsError(name) from error

    @classmethod
    def get_default_profile_name(cls, *, exclude_if_deleted: bool = True) -> str:
        """
        Get the name of default profile set.

        Raises
        ------
        NoDefaultProfileToLoadError: If no default profile is set.
        """
        if exclude_if_deleted and not cls.list_profiles():
            raise NoDefaultProfileToLoadError

        with cls.__open_database() as db:
            profile_name: str | None = db.get(cls._DEFAULT_PROFILE_IDENTIFIER, None)

        if profile_name is not None and profile_name != cls.ONBOARDING_PROFILE_NAME:
            return profile_name
        raise NoDefaultProfileToLoadError

    @classmethod
    def is_default_profile_set(cls) -> bool:
        try:
            cls.get_default_profile_name()
        except NoDefaultProfileToLoadError:
            return False
        return True

    @classmethod
    @contextmanager
    def __open_database(cls) -> Iterator[shelve.Shelf[Any]]:
        path = cls._get_file_storage_path()

        # create data directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with shelve.open(str(path)) as db:  # noqa: S301; TODO: handle that in the future
            yield db

    @classmethod
    def load(cls, name: str | None = None, *, auto_create: bool = True) -> ProfileData:
        """
        Load profile data with the given name from the database.

        Cases:
        1. if name=None and is_default_profile_set=True -> load default profile
        2. if name=None and is_default_profile_set=False -> raise error
        3. if name="some_name" and is_default_profile_set=True -> load "some_name"
        4. if name="some_name" and is_default_profile_set=False -> load "some_name".

        Args:
        ----
        name: Name of the profile to load. If None, the default profile is loaded.
        auto_create: If True, a new profile is created if the profile with the given name does not exist.

        Returns:
        -------
        Profile data.

        Raises:
        ------
        NoDefaultProfileToLoadError: If name is None but no default profile is set.
        ProfileDoesNotExistsError: If the profile does not exist and auto_create is False.
        """

        def create_new_profile(new_profile_name: str) -> ProfileData:
            if not auto_create:
                raise ProfileDoesNotExistsError(new_profile_name)
            return cls(new_profile_name)

        _name = name or cls.get_default_profile_name()

        with cls.__open_database() as db:
            stored_profile: ProfileData | None = db.get(_name, None)
            return stored_profile if stored_profile else create_new_profile(_name)

    @classmethod
    @asynccontextmanager
    async def load_with_auto_save(cls, name: str = "", *, auto_create: bool = True) -> AsyncIterator[ProfileData]:
        async with cls.load(name, auto_create=auto_create) as profile_data:
            yield profile_data

    @classmethod
    def list_profiles(cls) -> list[str]:
        """Get a list of all profiles sorted alphabetically."""
        with cls.__open_database() as db:
            return sorted(db.keys() - {cls._DEFAULT_PROFILE_IDENTIFIER})

    @staticmethod
    def __default_chain_id() -> str | None:
        chain_id = safe_settings.node.chain_id
        logger.info(f"Setting default chain_id to: {chain_id}")
        return chain_id

    @staticmethod
    def __default_node_address() -> list[Url]:
        return [
            Url("https", "api.hive.blog"),
            Url("https", "api.openhive.network"),
        ]

    @staticmethod
    def __get_secret_node_address() -> Url | None:
        return safe_settings.secrets.node_address
