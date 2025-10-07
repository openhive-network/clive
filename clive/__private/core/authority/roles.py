from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal, cast

from clive.__private.core.authority.authority_compound_regular import AuthorityCompoundRegular
from clive.__private.core.authority.authority_entries_holder import AuthorityEntriesHolder
from clive.__private.core.authority.entries import (
    AuthorityEntryAccountRegular,
    AuthorityEntryKeyRegular,
    AuthorityEntryMemo,
)
from clive.__private.core.str_utils import Matchable
from wax.complex_operations.role_classes.hive_authority.hive_role_authority_definition import (
    HiveRoleAuthorityDefinition,
)
from wax.complex_operations.role_classes.hive_authority.hive_role_memo_key import HiveRoleMemoKeyDefinition

if TYPE_CHECKING:
    from clive.__private.core.keys import KeyManager
    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.core.types import AuthorityLevel, AuthorityLevelMemo, AuthorityLevelRegular
    from clive.__private.models.schemas import AccountName

WaxRoleRegular = (
    HiveRoleAuthorityDefinition[Literal["owner"]]
    | HiveRoleAuthorityDefinition[Literal["active"]]
    | HiveRoleAuthorityDefinition[Literal["posting"]]
)
WaxRoleMemo = HiveRoleMemoKeyDefinition
WaxRole = WaxRoleRegular | WaxRoleMemo


class AuthorityRoleBase[T: (AuthorityCompoundRegular, AuthorityEntryMemo)](AuthorityEntriesHolder, Matchable, ABC):
    def __init__(self, role: WaxRole) -> None:
        self._role = role
        self._value: T = self._create_value()

    @abstractmethod
    def _create_value(self) -> T: ...

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
    def changed(self) -> bool:
        return self._role.changed

    @property
    def ensure_memo(self) -> AuthorityEntryMemo:
        assert self.is_memo, "Invalid type of entry."
        return cast("AuthorityEntryMemo", self)

    @property
    def ensure_regular(self) -> AuthorityCompoundRegular:
        assert not self.is_memo, "Invalid type of entry."
        return cast("AuthorityCompoundRegular", self)

    def is_matching_pattern(self, *patterns: str) -> bool:
        """
        Checks if any entry matches given pattern.

        Args:
            *patterns: Patterns to match against authority entries.

        Returns:
            True if any entry matches the pattern, False otherwise.
        """
        return any(entry.is_matching_pattern(*patterns) for entry in self.get_entries())

    def reset(self) -> None:
        self._role.reset()


class AuthorityRoleRegular(AuthorityRoleBase[AuthorityCompoundRegular]):
    def __init__(self, role: WaxRoleRegular) -> None:
        super().__init__(role)

    @property
    def role(self) -> WaxRoleRegular:
        return cast("WaxRoleRegular", super().role)

    @property
    def level(self) -> AuthorityLevelRegular:
        return cast("AuthorityLevelRegular", super().level)

    @property
    def weight_threshold(self) -> int:
        return self._value.weight_threshold
    
    def has(self, account_or_key: PublicKey | AccountName, weight: int | None = None) -> bool:
        return self.role.has(account_or_key, weight)

    def sum_weights_of_already_imported_keys(self, keys: KeyManager) -> int:
        """
        Sum weights for keys that are present in the key manager.

        Args:
            keys: Key manager instance to check against.

        Returns:
            Sum of weights for keys that are present in the key manager and this wrapper object.

        """
        return self._value.sum_weights_of_already_imported_keys(keys)

    def add(self, account_or_key: PublicKey | AccountName, weight: int) -> None:
        self._role.add(account_or_key, weight)

    def remove(self, account_or_key: PublicKey | AccountName) -> None:
        self._role.remove(account_or_key)

    def replace(
        self,
        account_or_key: PublicKey | AccountName,
        weight: int,
        new_account_or_key: PublicKey | AccountName | None = None,
    ) -> None:
        self._role.replace(account_or_key, weight, new_account_or_key)

    def set_threshold(self, threshold: int) -> None:
        self._role.set_threshold(threshold)

    def get_entries(self) -> list[AuthorityEntryKeyRegular | AuthorityEntryAccountRegular]:
        return self._value.get_entries()

    def _create_value(self) -> AuthorityCompoundRegular:
        return AuthorityCompoundRegular(self.role.value)


class AuthorityRoleMemo(AuthorityRoleBase[AuthorityEntryMemo]):
    def __init__(self, role: HiveRoleMemoKeyDefinition) -> None:
        super().__init__(role)

    @property
    def role(self) -> WaxRoleMemo:
        return cast("WaxRoleMemo", super().role)

    @property
    def level(self) -> AuthorityLevelMemo:
        return cast("AuthorityLevelMemo", super().level)

    @property
    def level_display(self) -> str:
        return "memo key"

    @property
    def is_memo(self) -> bool:
        return True

    def set(self, public_key: PublicKey) -> None:
        self._role.set(public_key)

    def get_entries(self) -> list[AuthorityEntryMemo]:
        return [self._value]

    def _create_value(self) -> AuthorityEntryMemo:
        return AuthorityEntryMemo(self.role.value)
