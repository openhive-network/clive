from __future__ import annotations

from abc import ABC
from typing import Any, Literal, Self, cast

from clive.__private.core.authority.authority_entries_holder import AuthorityEntriesHolder
from clive.__private.core.keys import PublicKey
from clive.__private.core.str_utils import Matchable, is_text_matching_pattern

AuthorityEntryKind = Literal["account", "key"]


class AuthorityEntryBase(AuthorityEntriesHolder, Matchable, ABC):
    def __init__(self, value: str, initial_value: str | None = None) -> None:
        self._value = value
        self._initial_value = initial_value if initial_value else value

    @property
    def value(self) -> str:
        return self._value

    @property
    def initial_value(self) -> str:
        return self._initial_value

    @property
    def is_weighted(self) -> bool:
        return False

    @property
    def is_key(self) -> bool:
        return False

    @property
    def is_account(self) -> bool:
        return False

    @property
    def ensure_weighted(self) -> AuthorityWeightedEntryBase:
        assert self.is_weighted, "Invalid type of entry."
        return cast("AuthorityWeightedEntryBase", self)

    @property
    def ensure_key(self) -> AuthorityEntryKeyBase:
        assert self.is_key, "Invalid type of entry."
        return cast("AuthorityEntryKeyBase", self)

    @property
    def ensure_account(self) -> AuthorityEntryAccountRegular:
        assert self.is_account, "Invalid type of entry."
        return cast("AuthorityEntryAccountRegular", self)

    def get_entries(self) -> list[Self]:
        return [self]

    def is_matching_pattern(self, *patterns: str) -> bool:
        """
        Checks if value of entry matches given pattern.

        Args:
            *patterns: Patterns to match against entry value.

        Returns:
            True if any value matches the pattern, False otherwise.

        """
        return is_text_matching_pattern(self.value, *patterns)

    @staticmethod
    def determine_entry_type(value: str) -> AuthorityEntryKind:
        return "key" if value.startswith("STM") else "account"


class AuthorityWeightedEntryBase(AuthorityEntryBase, ABC):
    def __init__(
        self, value: str, weight: int, initial_value: str | None = None, initial_weight: int | None = None
    ) -> None:
        super().__init__(value, initial_value)
        self._weight = weight
        self._initial_weight = initial_weight if initial_weight else weight

    @property
    def is_weighted(self) -> bool:
        return True

    @property
    def weight(self) -> int:
        return self._weight

    @property
    def initial_weight(self) -> int:
        return self._initial_weight


class AuthorityEntryKeyBase(AuthorityEntryBase, ABC):
    def __init__(self, key: str | PublicKey, *args: Any, **kwargs: Any) -> None:
        self._public_key = key if isinstance(key, PublicKey) else PublicKey(value=key)

        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(self._public_key.value, *args, **kwargs)

    @property
    def is_key(self) -> bool:
        return True

    @property
    def public_key(self) -> PublicKey:
        return self._public_key


class AuthorityEntryAccountRegular(AuthorityWeightedEntryBase):
    """
    Wrapper for account entries in authority.

    Args:
        account_name: The name of the account that authority entry represents.
        weight: The weight of the authority entry.
        initial_account_name: Initial name of the account that authority entry represents.
        initial_weight: Initial weight of the authority entry.
    """

    def __init__(
        self, account_name: str, weight: int, initial_account_name: str | None = None, initial_weight: int | None = None
    ) -> None:
        super().__init__(account_name, weight, initial_account_name, initial_weight)

    @property
    def is_account(self) -> bool:
        return True


class AuthorityEntryKeyRegular(AuthorityEntryKeyBase, AuthorityWeightedEntryBase):
    """
    Wrapper for key entries in authority.

    Args:
        key: The key that authority entry represents.
        weight: The weight of the authority entry.
        initial_key: Initial key that authority entry represents.
        initial_weight: Initial weight of the key.
    """

    def __init__(
        self, key: str | PublicKey, weight: int, initial_key: str | None = None, initial_weight: int | None = None
    ) -> None:
        super().__init__(key, weight, initial_key, initial_weight)


class AuthorityEntryMemo(AuthorityEntryKeyBase):
    """Wrapper for memo key entry in authority."""
