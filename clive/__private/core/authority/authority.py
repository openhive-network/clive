from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.authority_entries_holder import AuthorityEntriesHolder
from clive.__private.core.authority.roles import AuthorityRoleMemo, AuthorityRoleRegular
from clive.__private.core.str_utils import Matchable
from clive.__private.models.schemas import AccountUpdate2Operation
from clive.__private.models.transaction import Transaction

from __private.core.constants.node import NULL_ACCOUNT_KEY_VALUE

if TYPE_CHECKING:
    from clive.__private.core.authority.entries import (
        AuthorityEntryAccountRegular,
        AuthorityEntryKeyRegular,
        AuthorityEntryMemo,
    )
    from wax import IHiveChainInterface
    from wax.complex_operations.account_update import AccountAuthorityUpdateOperation
    from schemas.fields.compound import Authority as schema_authority


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
    
    def sync_operation_with_transaction(self, transaction: Transaction) -> None:
        """
        Synchronizes operation with given transaction. 
        
        Extracts AccountUpdate2Operations from transaction and modifies corresponding roles in operation.

        Args:
            transaction: transaction to synchronize with.
        """
        from clive.__private.logger import logger
        def extend_from_role(role_type: schema_authority | None, corresponding_role: AuthorityRoleRegular):
            if not role_type:
                return

            all_auths = role_type.account_auths + role_type.key_auths
            if role_type.weight_threshold != corresponding_role.weight_threshold:
                corresponding_role.set_threshold(role_type.weight_threshold)
            
            # remove something from operation if transaction doesnt have it

            all_entries_from_metaoperation = [entry for entry in corresponding_role.get_entries()]
            all_values_from_metaoperation = [entry.value for entry in all_entries_from_metaoperation]
            all_values_from_transaction = [auth[0] for auth in all_auths]
            for auth in all_auths: # single tuple
                value = auth[0] # value
                weight = auth[1] # weight

                 # add entry to operation if transaction have it
                if value not in all_values_from_metaoperation:
                    corresponding_role.add(value, weight)
                    logger.debug(f"SYNCING OPERATION WITH TRANSACTION: ADDING {value} {weight}")

                # check weights if entry is here and here, update if required
                if value in all_values_from_metaoperation:
                    for entry in all_entries_from_metaoperation:
                        if entry.value == value and entry.weight != weight:
                            corresponding_role.replace(value, weight)
                            logger.debug(f"SYNCING OPERATION WITH TRANSACTION: REPLACING {value} with new weight {weight}")

            # entry is present in metaoperation but not in transaction
            for value in all_values_from_metaoperation:
                if value not in all_values_from_transaction:
                    corresponding_role.remove(value)
                    logger.debug(f"SYNCING OPERATION WITH TRANSACTION: REMOVING {value}")
                

        account_update2_operations = [operation for operation in transaction.operations_models if isinstance(operation, AccountUpdate2Operation)]
        
        if not account_update2_operations:
            return
        
        for cart_operation in account_update2_operations:
            if cart_operation.account != self.account:
                continue
            
            # EXTRACT KEY AUTHS, ACCOUNT AUTHS WITH WEIGHTS, COMPARE WITH ROLE ENTRIES, FILL IF SOMETHING IS NOT PRESENT OR REMOVE!

            extend_from_role(cart_operation.owner, self.owner_role)
            extend_from_role(cart_operation.active, self.active_role)
            extend_from_role(cart_operation.posting, self.posting_role)

            if cart_operation.memo_key != self.memo_role.value:
                if cart_operation.memo_key == NULL_ACCOUNT_KEY_VALUE:
                    return
                self.memo_role.set(cart_operation.memo_key)
