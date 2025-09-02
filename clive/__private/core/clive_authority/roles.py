from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal, cast

from clive.__private.core.clive_authority.clive_authority_entries_holder import CliveAuthorityEntriesHolder
from clive.__private.core.clive_authority.clive_authority_regular import CliveAuthorityRegular
from clive.__private.core.clive_authority.entries import (
    CliveAuthorityEntryAccountRegular,
    CliveAuthorityEntryKeyRegular,
    CliveAuthorityEntryMemo,
)
from clive.__private.core.str_utils import Matchable
from wax.complex_operations.role_classes.hive_authority.hive_role_authority_definition import (
    HiveRoleAuthorityDefinition,
)
from wax.complex_operations.role_classes.hive_authority.hive_role_memo_key import HiveRoleMemoKeyDefinition

if TYPE_CHECKING:
    from clive.__private.core.clive_authority.types import AuthorityLevel, AuthorityLevelMemo, AuthorityLevelRegular
    from clive.__private.core.keys import KeyManager

WaxRoleRegular = (
    HiveRoleAuthorityDefinition[Literal["owner"]]
    | HiveRoleAuthorityDefinition[Literal["active"]]
    | HiveRoleAuthorityDefinition[Literal["posting"]]
)
WaxRoleMemo = HiveRoleMemoKeyDefinition
WaxRole = WaxRoleRegular | WaxRoleMemo


class CliveAuthorityRoleBase[T: (CliveAuthorityRegular, CliveAuthorityEntryMemo)](
    CliveAuthorityEntriesHolder, Matchable, ABC
):
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
    def ensure_memo(self) -> CliveAuthorityEntryMemo:
        assert self.is_memo, "Invalid type of entry."
        return cast("CliveAuthorityEntryMemo", self)

    @property
    def ensure_regular(self) -> CliveAuthorityRegular:
        assert not self.is_memo, "Invalid type of entry."
        return cast("CliveAuthorityRegular", self)

    def is_matching_pattern(self, *patterns: str) -> bool:
        return any(entry.is_matching_pattern(*patterns) for entry in self.get_entries())


class CliveAuthorityRoleRegular(CliveAuthorityRoleBase[CliveAuthorityRegular]):
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

    def sum_weights_of_already_imported_keys(self, keys: KeyManager) -> int:
        return self._value.sum_weights_of_already_imported_keys(keys)

    def get_entries(self) -> list[CliveAuthorityEntryKeyRegular | CliveAuthorityEntryAccountRegular]:
        return self._value.get_entries()

    def _create_value(self) -> CliveAuthorityRegular:
        return CliveAuthorityRegular(self.role.value)


class CliveAuthorityRoleMemo(CliveAuthorityRoleBase[CliveAuthorityEntryMemo]):
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

    def get_entries(self) -> list[CliveAuthorityEntryMemo]:
        return [self._value]

    def _create_value(self) -> CliveAuthorityEntryMemo:
        return CliveAuthorityEntryMemo(self.role.value)
