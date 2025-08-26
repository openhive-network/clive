from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.authority_entries_holder import AuthorityEntriesHolder
from clive.__private.core.authority.roles import AuthorityRoleMemo, AuthorityRoleRegular
from clive.__private.core.str_utils import Matchable

if TYPE_CHECKING:
    from clive.__private.core.authority.entries import (
        AuthorityEntryAccountRegular,
        AuthorityEntryKeyRegular,
        AuthorityEntryMemo,
    )
    from wax.complex_operations.account_update import AccountAuthorityUpdateOperation


class Authority(AuthorityEntriesHolder, Matchable):
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
    def owner_role(self) -> AuthorityRoleRegular:
        return AuthorityRoleRegular(self.operation.roles.owner)

    @property
    def active_role(self) -> AuthorityRoleRegular:
        return AuthorityRoleRegular(self.operation.roles.active)

    @property
    def posting_role(self) -> AuthorityRoleRegular:
        return AuthorityRoleRegular(self.operation.roles.posting)

    @property
    def memo_role(self) -> AuthorityRoleMemo:
        return AuthorityRoleMemo(self.operation.roles.memo)

    @property
    def roles(self) -> list[AuthorityRoleRegular | AuthorityRoleMemo]:
        return [self.owner_role, self.active_role, self.posting_role, self.memo_role]

    def get_entries(
        self,
    ) -> list[AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo]:
        return [entry for role in self.roles for entry in role.get_entries()]

    def is_matching_pattern(self, *patterns: str) -> bool:
        """
        Checks if any role matches given pattern.

        Args:
            *patterns: Patterns to match against authority entries.

        Returns:
            True if any role matches the pattern, False otherwise.
        """
        return any(role.is_matching_pattern(*patterns) for role in self.roles)
