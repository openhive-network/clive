from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.entries import (
    AuthorityEntryAccountRegular,
    AuthorityEntryKeyRegular,
)
from clive.__private.core.str_utils import Matchable

if TYPE_CHECKING:
    from clive.__private.core.keys import KeyManager
    from wax.models.authority import WaxAuthority


class AuthorityCompoundRegular(Matchable):
    """
    A wrapper to provide utility methods for wax authority objects.

    Args:
        authority: Wax authority object to wrap.
    """

    def __init__(self, authority: WaxAuthority) -> None:
        super().__init__()
        self._authority = authority

    @property
    def authority(self) -> WaxAuthority:
        return self._authority

    @property
    def account_entries(self) -> list[AuthorityEntryAccountRegular]:
        return [
            AuthorityEntryAccountRegular(account, weight) for account, weight in self._authority.account_auths.items()
        ]

    @property
    def key_entries(self) -> list[AuthorityEntryKeyRegular]:
        return [AuthorityEntryKeyRegular(key, weight) for key, weight in self._authority.key_auths.items()]

    @property
    def all_entries(self) -> list[AuthorityEntryAccountRegular | AuthorityEntryKeyRegular]:
        return self.get_entries()

    @property
    def weight_threshold(self) -> int:
        return self._authority.weight_threshold

    def get_entries(self) -> list[AuthorityEntryAccountRegular | AuthorityEntryKeyRegular]:
        return self.account_entries + self.key_entries

    def is_matching_pattern(self, *patterns: str) -> bool:
        """
        Checks if any entry matches given pattern.

        Args:
            *patterns: Patterns to match against authority entries.

        Returns:
            True if any entry matches the pattern, False otherwise.
        """
        return any(entry_wrapper_object.is_matching_pattern(*patterns) for entry_wrapper_object in self.get_entries())

    def sum_weights_of_already_imported_keys(self, keys: KeyManager) -> int:
        """
        Sum weights for keys that are present in the key manager.

        Args:
            keys: Key manager instance to check against.

        Returns:
            Sum of weights for keys that are present in the key manager and this wrapper object.

        """
        entries = self.key_entries
        return sum(entry.weight for entry in entries if entry.public_key in keys)
