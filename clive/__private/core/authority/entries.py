from __future__ import annotations

from abc import ABC
from typing import Any, Literal, Self, cast

from clive.__private.core.authority.authority_entries_holder import AuthorityEntriesHolder
from clive.__private.core.keys import PublicKey
from clive.__private.core.str_utils import Matchable, is_text_matching_pattern
from clive.__private.logger import logger

AuthorityEntryKind = Literal["account", "key"]


class AuthorityEntryBase(AuthorityEntriesHolder, Matchable, ABC):
    def __init__(self, value: str) -> None:
        self._value = value
        self._initial_value = value
        logger.debug(f"AUTHORITY ENTRY BASE CLASS OBJECT CREATED WITH VALUE: {value}.")

    @property
    def value(self) -> str:
        return self._value
    
    @property
    def initial_value(self) -> int:
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
    
    def restore(self) -> None:
        """Restores entry to its initial values."""
        self._value = self._initial_value

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

    def update_value(self, new_value: str) -> None:
        self._value = new_value

    @staticmethod
    def determine_entry_type(value: str) -> AuthorityEntryKind:
        return "key" if value.startswith("STM") else "account"


class AuthorityWeightedEntryBase(AuthorityEntryBase, ABC):
    def __init__(self, value: str, weight: int) -> None:
        super().__init__(value)
        self._weight = weight
        self._initial_weight = weight

    @property
    def is_weighted(self) -> bool:
        return True

    @property
    def weight(self) -> int:
        return self._weight
    
    @property
    def initial_weight(self) -> int:
        return self._initial_weight
    
    def restore(self) -> None:
        self._value = self._initial_value
        self._weight = self._initial_weight

    def update_weight(self, new_weight: int) -> None:
        self._weight = new_weight


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
    """

    def __init__(self, account_name: str, weight: int) -> None:
        super().__init__(account_name, weight)

    @property
    def is_account(self) -> bool:
        return True


class AuthorityEntryKeyRegular(AuthorityEntryKeyBase, AuthorityWeightedEntryBase):
    """
    Wrapper for key entries in authority.

    Args:
        key: The key that authority entry represents.
        weight: The weight of the authority entry.
    """

    def __init__(self, key: str | PublicKey, weight: int) -> None:
        super().__init__(key, weight)


class AuthorityEntryMemo(AuthorityEntryKeyBase):
    """Wrapper for memo key entry in authority."""
