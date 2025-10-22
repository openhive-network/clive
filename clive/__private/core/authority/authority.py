from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.authority_entries_holder import AuthorityEntriesHolder
from clive.__private.core.authority.roles import AuthorityRoleMemo, AuthorityRoleRegular
from clive.__private.core.str_utils import Matchable
from clive.__private.models.schemas import AccountUpdate2Operation
from clive.__private.models.transaction import Transaction

if TYPE_CHECKING:
    from clive.__private.core.authority.entries import (
        AuthorityEntryAccountRegular,
        AuthorityEntryKeyRegular,
        AuthorityEntryMemo,
    )
    from wax import IHiveChainInterface
    from wax.complex_operations.account_update import AccountAuthorityUpdateOperation


class Authority(AuthorityEntriesHolder, Matchable):
    """
    Wrapper for account authority update operation from wax.

    Args:
        operation: The account authority update operation to wrap.
    """

    def __init__(self, operation: AccountAuthorityUpdateOperation) -> None:
        self._operation = operation
        self._owner_role = AuthorityRoleRegular(self.operation.roles.owner)
        self._active_role = AuthorityRoleRegular(self.operation.roles.active)
        self._posting_role = AuthorityRoleRegular(self.operation.roles.posting)
        self._memo_role = AuthorityRoleMemo(self.operation.roles.memo)

    @property
    def operation(self) -> AccountAuthorityUpdateOperation:
        return self._operation

    @property
    def account(self) -> str:
        return self.operation.categories.hive.account

    @property
    def owner_role(self) -> AuthorityRoleRegular:
        return self._owner_role

    @property
    def active_role(self) -> AuthorityRoleRegular:
        return self._active_role

    @property
    def posting_role(self) -> AuthorityRoleRegular:
        return self._posting_role

    @property
    def memo_role(self) -> AuthorityRoleMemo:
        return self._memo_role

    @property
    def roles(self) -> list[AuthorityRoleRegular | AuthorityRoleMemo]:
        return [self._owner_role, self._active_role, self._posting_role, self._memo_role]

    def get_entries(
        self,
    ) -> list[AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo]:
        return [entry for role in self.roles for entry in role.get_entries()]

    def reset(self) -> None:
        for role in self.roles:
            role.reset()

    def is_matching_pattern(self, *patterns: str) -> bool:
        """
        Checks if any role matches given pattern.

        Args:
            *patterns: Patterns to match against authority entries.

        Returns:
            True if any role matches the pattern, False otherwise.
        """
        return any(role.is_matching_pattern(*patterns) for role in self.roles)

    def finalize(self, api: IHiveChainInterface) -> AccountUpdate2Operation:
        # `tapos_block_id` can have any value, since the operation will be extracted
        # from the transaction anyway, and TAPOS are irrelevant.
        wax_transaction = api.create_transaction_with_tapos(tapos_block_id="123456")
        wax_transaction.push_operation(self._operation)

        wax_transaction_json = wax_transaction.to_api_json()
        clive_transaction = Transaction.parse_raw(wax_transaction_json)

        clive_operations = clive_transaction.operations
        assert len(clive_operations) == 1, "Expected exactly one operation in the transaction"

        clive_operation = clive_operations[0].value
        assert isinstance(clive_operation, AccountUpdate2Operation), "Operation type is other than expected."

        return clive_operation
