from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from clive.__private.core.accounts.accounts import Account, ExchangeAccount
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Iterator

ExchangeEntity = Literal["Binance", "Upbit", "HTX", "MEXC"]


class KnownExchangeError(CliveError):
    """Base error for all known exchange related errors."""


class KnownExchangeNotFoundError(KnownExchangeError):
    """Raised when a known exchange is not found."""


class KnownExchanges:
    """
    A container-like object, that manages a known exchange accounts.

    Container is a read-only object that allows you to check whether the accounts are known exchange accounts
    or to obtain detailed information about them.
    """

    def __init__(self) -> None:
        self._exchanges: set[ExchangeAccount] = {
            ExchangeAccount(name="bdhivesteem", entity="Binance"),
            ExchangeAccount(name="deepcrypto8", entity="Binance"),
            ExchangeAccount(name="user.dunamu", entity="Upbit"),
            ExchangeAccount(name="huobi-pro", entity="HTX"),
            ExchangeAccount(name="mxchive", entity="MEXC"),
        }

    def __iter__(self) -> Iterator[ExchangeAccount]:
        return iter(self._exchanges)

    def __len__(self) -> int:
        return len(self._exchanges)

    def __bool__(self) -> bool:
        return bool(self._exchanges)

    def __contains__(self, account: str | Account | ExchangeAccount) -> bool:
        """
        Check if the account is a known exchange.

        Args:
            account: Account name or instance to check for.

        Returns:
            True if the account is a known exchange, False otherwise.
        """
        account_name = Account.ensure_account_name(account)

        return any(account_name == exchange.name for exchange in self._exchanges)

    def get_by_account_name(self, account: str | Account) -> ExchangeAccount:
        """
        Get an exchange account by its name.

        Args:
            account: Account name to search for. Can be obtained from the account instance.

        Raises:
            KnownExchangeNotFoundError: if the account is not known exchange.

        Returns:
            The exchange account with the given account name.
        """
        account_name = Account.ensure_account_name(account)

        for exchange in self._exchanges:
            if account_name == exchange.name:
                return exchange

        raise KnownExchangeNotFoundError(f"Known exchange with account name: {account_name} not found.")

    def get_entity_by_account_name(self, account: str | Account) -> ExchangeEntity:
        """
        Get an exchange entity by its name.

        Args:
            account: Account name to search for. Can be obtained from the account instance.

        Raises:
            KnownExchangeAccountNotFoundError: if the account is not known exchange.

        Returns:
            The entity name of the exchange account.
        """
        return self.get_by_account_name(account).entity

    def get_account_name_by_entity(self, entity: ExchangeEntity) -> str:
        """
        Get an exchange account name by its entity.

        Args:
            entity: Entity of the exchange to search for.

        Raises:
            KnownExchangeNotFoundError: if known exchange with the given entity is not found.

        Returns:
            The account name associated with the given exchange entity.
        """
        for exchange in self._exchanges:
            if exchange.entity == entity:
                return exchange.name

        raise KnownExchangeNotFoundError(f"Known exchange with entity: {entity} not found.")
