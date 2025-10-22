from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Literal, cast

from clive.__private.core.authority.authority_entries_holder import AuthorityEntriesHolder
from clive.__private.core.authority.entries import (
    AuthorityEntryAccountRegular,
    AuthorityEntryKeyRegular,
    AuthorityEntryMemo,
)
from clive.__private.core.authority.exceptions import EntryNotFoundError
from clive.__private.core.str_utils import Matchable
from wax.complex_operations.role_classes.hive_authority.hive_role_authority_definition import (
    HiveRoleAuthorityDefinition,
)
from wax.complex_operations.role_classes.hive_authority.hive_role_memo_key import HiveRoleMemoKeyDefinition

if TYPE_CHECKING:
    from clive.__private.core.keys import KeyManager
    from clive.__private.core.types import AuthorityLevel, AuthorityLevelMemo, AuthorityLevelRegular
    from wax.models.authority import WaxAuthority

WaxRoleRegular = (
    HiveRoleAuthorityDefinition[Literal["owner"]]
    | HiveRoleAuthorityDefinition[Literal["active"]]
    | HiveRoleAuthorityDefinition[Literal["posting"]]
)
WaxRoleMemo = HiveRoleMemoKeyDefinition
WaxRole = WaxRoleRegular | WaxRoleMemo


class AuthorityRoleBase(AuthorityEntriesHolder, Matchable, ABC):
    def __init__(self, role: WaxRole) -> None:
        self._role = role

    @property
    def role(self) -> WaxRole:
        return self._role

    @property
    def level(self) -> AuthorityLevel:
        return self._role.level

    @property
    def level_display(self) -> str:
        return str(self.level)

    @property
    def is_memo(self) -> bool:
        return False

    @property
    def is_regular(self) -> bool:
        return False

    @property
    def is_changed(self) -> bool:
        return self._role.changed

    @property
    def ensure_memo(self) -> AuthorityRoleMemo:
        assert self.is_memo, "Invalid type of entry."
        return cast("AuthorityRoleMemo", self)

    @property
    def ensure_regular(self) -> AuthorityRoleRegular:
        assert self.is_regular, "Invalid type of entry."
        return cast("AuthorityRoleRegular", self)

    def is_matching_pattern(self, *patterns: str) -> bool:
        """
        Checks if any entry matches given pattern.

        Args:
            *patterns: Patterns to match against authority entries.

        Returns:
            True if any entry matches the pattern, False otherwise.
        """
        return any(entry.is_matching_pattern(*patterns) for entry in self.get_entries())


class AuthorityRoleRegular(AuthorityRoleBase):
    @property
    def authority(self) -> WaxAuthority:
        return self.role.value

    @property
    def role(self) -> WaxRoleRegular:
        return cast("WaxRoleRegular", super().role)

    @property
    def is_regular(self) -> bool:
        return True

    @property
    def level(self) -> AuthorityLevelRegular:
        return cast("AuthorityLevelRegular", super().level)

    @property
    def weight_threshold(self) -> int:
        return self.authority.weight_threshold

    @property
    def is_null_authority(self) -> bool:
        return self.role.is_null_authority

    @property
    def account_entries(self) -> list[AuthorityEntryAccountRegular]:
        return [
            AuthorityEntryAccountRegular(account, weight) for account, weight in self.authority.account_auths.items()
        ]

    @property
    def key_entries(self) -> list[AuthorityEntryKeyRegular]:
        return [AuthorityEntryKeyRegular(key, weight) for key, weight in self.authority.key_auths.items()]

    @property
    def all_entries(self) -> list[AuthorityEntryAccountRegular | AuthorityEntryKeyRegular]:
        return self.get_entries()

    def get_entries(self) -> list[AuthorityEntryAccountRegular | AuthorityEntryKeyRegular]:
        return self.account_entries + self.key_entries

    def get_entry(self, value: str) -> AuthorityEntryAccountRegular | AuthorityEntryKeyRegular:
        for entry in self.all_entries:
            if entry.value == value:
                return entry
        raise EntryNotFoundError(value)

    def is_matching_pattern(self, *patterns: str) -> bool:
        """
        Checks if any entry matches given pattern.

        Args:
            *patterns: Patterns to match against authority entries.

        Returns:
            True if any entry matches the pattern, False otherwise.
        """
        return any(entry_wrapper_object.is_matching_pattern(*patterns) for entry_wrapper_object in self.get_entries())

    def add(self, account_or_key: str, weight: int) -> None:
        self.role.add(account_or_key, weight)

    def remove(self, account_or_key: str) -> None:
        self.role.remove(account_or_key)

    def replace(
        self,
        account_or_key: str,
        weight: int,
        new_account_or_key: str | None = None,
    ) -> None:
        self.role.replace(account_or_key, weight, new_account_or_key)

    def set_threshold(self, threshold: int) -> None:
        self.role.set_threshold(threshold)

    def has(self, account_or_key: str, weight: int | None = None) -> bool:
        return self.role.has(account_or_key, weight)

    def reset(self) -> None:
        self._role.reset()

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


class AuthorityRoleMemo(AuthorityRoleBase):
    @property
    def role(self) -> WaxRoleMemo:
        return cast("WaxRoleMemo", super().role)

    @property
    def entry(self) -> AuthorityEntryMemo:
        return AuthorityEntryMemo(self.role.value)

    @property
    def level(self) -> AuthorityLevelMemo:
        return cast("AuthorityLevelMemo", super().level)

    @property
    def level_display(self) -> str:
        return "memo key"

    @property
    def is_memo(self) -> bool:
        return True

    def set(self, public_key: str) -> None:
        self.role.set(public_key)

    def reset(self) -> None:
        self._role.reset()

    def get_entries(self) -> list[AuthorityEntryMemo]:
        return [self.entry]
