from __future__ import annotations

from collections.abc import Iterator
from typing import Literal

from clive.__private.core.accounts.accounts import Account, ExchangeAccount
from clive.exceptions import CliveError

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
        """Check if the account is a known exchange."""
        account_name = Account.ensure_account_name(account)

        return any(account_name == exchange.name for exchange in self._exchanges)

    def get_by_account_name(self, account: str | Account) -> ExchangeAccount:
        """
        Get an exchange account by its name.

        Raises
        ------
        KnownExchangeNotFoundError: if the account is not known exchange.
        """
        account_name = Account.ensure_account_name(account)

        for exchange in self._exchanges:
            if account_name == exchange.name:
                return exchange

        raise KnownExchangeNotFoundError(f"Known exchange with account name: {account_name} not found.")

    def get_entity_by_account_name(self, account: str | Account) -> ExchangeEntity:
        """
        Get an exchange entity by its name.

        Raises
        ------
        KnownExchangeAccountNotFoundError: if the account is not known exchange.
        """
        return self.get_by_account_name(account).entity

    def get_account_name_by_entity(self, entity: ExchangeEntity) -> str:
        """
        Get an exchange account name by its entity.

        Raises
        ------
        KnownExchangeNotFoundError: if known exchange with the given entity is not found.
        """
        for exchange in self._exchanges:
            if exchange.entity == entity:
                return exchange.name

        raise KnownExchangeNotFoundError(f"Known exchange with entity: {entity} not found.")
