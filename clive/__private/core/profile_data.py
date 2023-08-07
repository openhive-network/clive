from __future__ import annotations

import shelve
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from clive.__private import config
from clive.__private.storage.contextual import Context
from clive.core.url import Url
from clive.exceptions import CliveError
from clive.models import Operation

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from clive.__private.storage.accounts import Account, WorkingAccount


class ProfileDataError(CliveError):
    """An error related to profile data."""


class NoWorkingAccountError(ProfileDataError):
    """No working account is available."""


class ProfileCouldNotBeLoadedError(ProfileDataError):
    """Raised when a profile could not be loaded."""


class ProfileDoesNotExistsError(ProfileCouldNotBeLoadedError):
    def __init__(self, profile_name: str) -> None:
        super().__init__(f"Profile `{profile_name}` does not exist.")


class NoLastlyUsedProfileError(ProfileCouldNotBeLoadedError):
    """Raised when no lastly used profile exists."""


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
        self._working_account = working_account
        self.watched_accounts = set(watched_accounts or [])
        self.known_accounts = set(known_accounts or [])

        self.cart = Cart()

        self.backup_node_addresses = self.__default_node_address()
        self._node_address = self.backup_node_addresses[0]

    @property
    def working_account(self) -> WorkingAccount:
        """
        Returns the working account.

        Raises
        ------
        NoWorkingAccountError: If no working account is set.
        """
        if self._working_account is None:
            raise NoWorkingAccountError
        return self._working_account

    @working_account.setter
    def working_account(self, value: WorkingAccount) -> None:
        self._working_account = value

    @property
    def node_address(self) -> Url:
        return self._node_address

    @classmethod
    def _get_file_storage_path(cls) -> Path:
        return Path(config.settings.data_path) / "data/profile"

    def save(self) -> None:
        from clive.__private.ui.app import Clive

        if Clive.is_app_exist():
            Clive.app_instance().world.update_reactive("profile_data")

        with self.__open_database() as db:
            db[self.name] = self
            db[self._LAST_USED_IDENTIFIER] = self.name

    @classmethod
    def get_lastly_used_profile_name(cls) -> str | None:
        """Get the name of the lastly used profile. If no profile was used yet, None is returned."""
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
        ProfileCouldNotBeLoadedError: If the profile could not be loaded.
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
    def list_profiles(cls) -> list[str]:
        with cls.__open_database() as db:
            return list(db.keys() - {cls._LAST_USED_IDENTIFIER})

    @staticmethod
    def __default_node_address() -> list[Url]:
        return [
            Url("http", "localhost", 8090),
            Url("https", "api.hive.blog"),
            Url("http", "hive-6.pl.syncad.com", 18090),
        ]
