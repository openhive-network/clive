from __future__ import annotations

import shelve
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from clive.__private import config
from clive.__private.config import settings
from clive.__private.core.clive_import import get_clive
from clive.__private.storage.accounts import WorkingAccount
from clive.__private.storage.contextual import Context
from clive.core.url import Url
from clive.exceptions import CliveError
from clive.models import Operation

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from types import TracebackType

    from typing_extensions import Self

    from clive.__private.storage.accounts import Account


class ProfileDataError(CliveError):
    """An error related to profile data."""


class NoWorkingAccountError(ProfileDataError):
    """No working account is available."""


class ProfileCouldNotBeLoadedError(ProfileDataError):
    """Raised when a profile could not be loaded."""


class ProfileCouldNotBeDeletedError(ProfileDataError):
    """Raised when a profile could not be deleted."""


class ProfileDoesNotExistsError(ProfileCouldNotBeLoadedError, ProfileCouldNotBeDeletedError):
    def __init__(self, profile_name: str) -> None:
        super().__init__(f"Profile `{profile_name}` does not exist.")


class NoLastlyUsedProfileError(ProfileCouldNotBeLoadedError):
    """Raised when no lastly used profile exists."""


class ProfileSaveError(ProfileDataError):
    """Raised when a profile could not be saved."""


class ProfileAlreadyExistsError(ProfileDataError):
    """Raised when a profile already exists."""


class Cart(list[Operation]):
    def swap(self, index_1: int, index_2: int) -> None:
        self[index_1], self[index_2] = self[index_2], self[index_1]


class ProfileData(Context):
    ONBOARDING_PROFILE_NAME: Final[str] = "onboarding"
    _LAST_USED_IDENTIFIER: Final[str] = "!last_used"

    def __init__(
        self,
        name: str,
        working_account: WorkingAccount | None = None,
        watched_accounts: Iterable[Account] | None = None,
        known_accounts: Iterable[Account] | None = None,
    ) -> None:
        self.name = name
        self.__working_account = working_account
        self.watched_accounts = set(watched_accounts or [])
        self.known_accounts = set(known_accounts or [])

        self.cart = Cart()

        if address := self.__get_secret_node_address():
            self.backup_node_addresses = [address]
            self.__node_address = address
        else:
            self.backup_node_addresses = self.__default_node_address()
            self.__node_address = self.backup_node_addresses[0]

        self.__first_time_save = True
        self.__skip_save = False

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _: type[Exception] | None, __: Exception | None, ___: TracebackType | None) -> None:
        self.save()

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

    def set_working_account(self, value: str | WorkingAccount) -> None:
        if isinstance(value, str):
            value = WorkingAccount(value)
        self.__working_account = value

    def unset_working_account(self) -> None:
        self.__working_account = None

    @property
    def node_address(self) -> Url:
        return self.__get_secret_node_address() or self.__node_address

    def _set_node_address(self, value: Url) -> None:
        """
        Set the node address.

        It is marked as not intended for usage because you rather should use Node.set_address instead.
        """
        self.__node_address = value

    def is_working_account_set(self) -> bool:
        return self.__working_account is not None

    def get_tracked_accounts(self) -> set[Account]:
        accounts = self.watched_accounts.copy()
        if self.is_working_account_set():
            accounts.add(self.working_account)
        return accounts

    @classmethod
    def _get_file_storage_path(cls) -> Path:
        return Path(config.settings.data_path) / "data/profile"

    def save(self) -> None:
        if self.__skip_save:
            return

        if self.__first_time_save and self.name in self.list_profiles():
            raise ProfileAlreadyExistsError(
                f"Profile `{self.name}` already exists. Please choose another name, different than"
                f" {self.list_profiles()}"
            )
        self.__first_time_save = False

        clive = get_clive().app_instance()

        if clive.is_launched:
            clive.world.update_reactive("profile_data")

        with self.__open_database() as db:
            db[self.name] = self
            db[self._LAST_USED_IDENTIFIER] = self.name

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
    def get_lastly_used_profile_name(cls, *, exclude_if_deleted: bool = True) -> str | None:
        """Get the name of the lastly used profile. If no profile was used yet, None is returned."""
        if exclude_if_deleted and not cls.list_profiles():
            return None

        with cls.__open_database() as db:
            profile_name: str | None = db.get(cls._LAST_USED_IDENTIFIER, None)
            if profile_name != cls.ONBOARDING_PROFILE_NAME:
                return profile_name
            return None

    @classmethod
    @contextmanager
    def __open_database(cls) -> Iterator[shelve.Shelf[Any]]:
        path = cls._get_file_storage_path()

        # create data directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with shelve.open(str(path)) as db:
            yield db

    @classmethod
    def load(cls, name: str = "", *, auto_create: bool = True) -> ProfileData:
        """
        Load profile data with the given name from the database.

        Args:
        ----
        name: Name of the profile to load. If empty, the lastly used profile is loaded.
        auto_create: If True, a new profile is created if the profile with the given name does not exist.

        Returns:
        -------
        Profile data.

        Raises:
        ------
        NoLastlyUsedProfileError: If name is empty but no lastly used profile exists.
        ProfileDoesNotExistsError: If the profile does not exist and auto_create is False.
        """

        def assert_profile_could_be_loaded() -> None:
            """
            Assert that the profile with the given name could be loaded.

            Cases:
            1. name="" and lastly_used_exists=True -> load lastly_used
            2. name="" and lastly_used_exists=False -> raise error
            3. name="some_name" and lastly_used_exists=True -> load "some_name"
            4. name="some_name" and lastly_used_exists=False -> load "some_name".
            """
            lastly_used_exists = cls.get_lastly_used_profile_name()
            if not lastly_used_exists and not name:
                raise NoLastlyUsedProfileError

        def create_new_profile(new_profile_name: str) -> ProfileData:
            if not auto_create:
                raise ProfileDoesNotExistsError(new_profile_name)
            return cls(new_profile_name)

        assert_profile_could_be_loaded()

        with cls.__open_database() as db:
            if not name:
                name = cls.get_lastly_used_profile_name()  # type: ignore[assignment]
                assert name is not None, "We already checked that lastly used profile exists."

            stored_profile: ProfileData | None = db.get(name, None)
            return stored_profile if stored_profile else create_new_profile(name)

    @classmethod
    @contextmanager
    def load_with_auto_save(cls, name: str = "", *, auto_create: bool = True) -> Iterator[ProfileData]:
        with cls.load(name, auto_create=auto_create) as profile_data:
            yield profile_data

    @classmethod
    def list_profiles(cls) -> list[str]:
        with cls.__open_database() as db:
            return list(db.keys() - {cls._LAST_USED_IDENTIFIER})

    @staticmethod
    def __default_node_address() -> list[Url]:
        return [
            Url("https", "api.hive.blog"),
            Url("https", "api.openhive.network"),
            Url("https", "api.deathwing.me"),
            Url("https", "hive-api.arcange.eu"),
        ]

    @staticmethod
    def __get_secret_node_address() -> Url | None:
        node_address = settings.get("secrets.node_address", None)
        return Url.parse(node_address) if node_address else None
