from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.clive_authority.clive_authority_entries_holder import CliveAuthorityEntriesHolder
from clive.__private.core.clive_authority.roles import CliveAuthorityRoleMemo, CliveAuthorityRoleRegular
from clive.__private.core.str_utils import Matchable

if TYPE_CHECKING:
    from clive.__private.core.clive_authority.entries import (
        CliveAuthorityEntryAccountRegular,
        CliveAuthorityEntryKeyRegular,
        CliveAuthorityEntryMemo,
    )
    from wax.complex_operations.account_update import AccountAuthorityUpdateOperation


class CliveAuthority(CliveAuthorityEntriesHolder, Matchable):
    """
    Wrapper for account authority update operation from wax.

    Args:
        operation: The account authority update operation to wrap.
    """

    def __init__(self, operation: AccountAuthorityUpdateOperation) -> None:
        self._operation = operation

    @property
    def operation(self) -> AccountAuthorityUpdateOperation:
        return self._operation

    @property
    def account(self) -> str:
        return self.operation.categories.hive.account

    @property
    def owner_role(self) -> CliveAuthorityRoleRegular:
        return CliveAuthorityRoleRegular(self.operation.roles.owner)

    @property
    def active_role(self) -> CliveAuthorityRoleRegular:
        return CliveAuthorityRoleRegular(self.operation.roles.active)

    @property
    def posting_role(self) -> CliveAuthorityRoleRegular:
        return CliveAuthorityRoleRegular(self.operation.roles.posting)

    @property
    def memo_role(self) -> CliveAuthorityRoleMemo:
        return CliveAuthorityRoleMemo(self.operation.roles.memo)

    @property
    def roles(self) -> list[CliveAuthorityRoleRegular | CliveAuthorityRoleMemo]:
        return [self.owner_role, self.active_role, self.posting_role, self.memo_role]

    def get_entries(
        self,
    ) -> list[CliveAuthorityEntryKeyRegular | CliveAuthorityEntryAccountRegular | CliveAuthorityEntryMemo]:
        return [entry for role in self.roles for entry in role.get_entries()]

    def is_matching_pattern(self, *patterns: str) -> bool:
        return any(role.is_matching_pattern(*patterns) for role in self.roles)
