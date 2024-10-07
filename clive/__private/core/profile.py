from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from clive.__private.core.accounts.account_manager import AccountManager
from clive.__private.core.constants.profile import PROFILE_ENCRYPTION_WALLET_SUFFIX
from clive.__private.core.contextual import Context
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.core.keys import KeyManager, PublicKeyAliased
from clive.__private.core.url import Url
from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.models.schemas import ChainId, OperationBase
from clive.__private.settings import safe_settings
from clive.__private.validators.profile_name_validator import ProfileNameValidator
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import TracebackType

    from typing_extensions import Self

    from clive.__private.core.accounts.accounts import Account, KnownAccount, WatchedAccount, WorkingAccount


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


class Cart(list[OperationBase]):
    def swap(self, index_1: int, index_2: int) -> None:
        self[index_1], self[index_2] = self[index_2], self[index_1]


def encryption_wallet_name(profile_name: str) -> str:
    return f"{profile_name}{PROFILE_ENCRYPTION_WALLET_SUFFIX}"


def encryption_key_alias(profile_name: str) -> str:
    return f"{profile_name}{PROFILE_ENCRYPTION_WALLET_SUFFIX}"


class Profile(Context):
    def __init__(
        self,
        name: str,
        working_account: str | Account | None = None,
        watched_accounts: Iterable[str | Account] | None = None,
        known_accounts: Iterable[str | Account] | None = None,
    ) -> None:
        self.validate_profile_name(name)
        self.name = name
        self.cart = Cart()
        self.keys = KeyManager()

        self._encryption_key: PublicKeyAliased | None = None
        self._accounts = AccountManager(working_account, watched_accounts, known_accounts)
        self._backup_node_addresses = self._default_node_address()
        self._set_node_address(self._initial_node_address())
        self._chain_id = self._default_chain_id()

        self._is_newly_created = True

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, __: BaseException | None, ___: TracebackType | None
    ) -> None:
        pass

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
        if not is_schema_field_valid(ChainId, value):
            raise InvalidChainIdError

        self._chain_id = value

    @property
    def encryption_key(self) -> PublicKeyAliased:
        assert self._encryption_key, "encryption_key is not set"
        return self._encryption_key

    def set_encryption_key(self, key: PublicKeyAliased) -> None:
        self._encryption_key = key

    def unset_chain_id(self) -> None:
        """When no chain_id is set, it should be fetched from the node api."""
        self._chain_id = None

    def copy(self) -> Self:
        return deepcopy(self)

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
        cart_operations: Iterable[OperationBase] | None = None,
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
