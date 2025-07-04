from __future__ import annotations

import re

from clive.__private.core.keys.key_manager import KeyManager
from clive.__private.core.keys.keys import PublicKey
from wax.complex_operations.account_update import AccountAuthorityUpdateOperation
from wax.complex_operations.role_classes.hive_authority.hive_account_category import HiveAccountCategory
from wax.complex_operations.role_classes.hive_authority.hive_role_authority_definition import (
    HiveRoleAuthorityDefinition,
)
from wax.complex_operations.role_classes.hive_authority.hive_role_memo_key import HiveRoleMemoKeyDefinition
from wax.complex_operations.role_classes.hive_authority.hive_roles import ActiveRoleName, OwnerRoleName, PostingRoleName
from wax.complex_operations.role_classes.level_base import TRole
from wax.models.authority import WaxAuthority


def is_match(text: str, *patterns: str) -> bool:
    return any(re.search(re.escape(pattern), text) for pattern in patterns)


class CliveAuthority:
    """Wrapper for AccountAuthorityUpdateOperation from wax."""

    def __init__(self, operation: AccountAuthorityUpdateOperation) -> None:
        self._operation = operation

    @property
    def account(self) -> str:
        return self._operation.categories.hive.account

    @property
    def active(self) -> HiveRoleAuthorityDefinition[ActiveRoleName]:
        return AuthorityRoleWrapper(self._operation.roles.active)

    @property
    def memo(self) -> HiveRoleMemoKeyDefinition:
        return AuthorityRoleWrapper(self._operation.roles.memo)

    @property
    def owner(self) -> HiveRoleAuthorityDefinition[OwnerRoleName]:
        return AuthorityRoleWrapper(self._operation.roles.owner)

    @property
    def posting(self) -> HiveRoleAuthorityDefinition[PostingRoleName]:
        return AuthorityRoleWrapper(self._operation.roles)

    @property
    def roles(self) -> HiveAccountCategory:
        return [AuthorityRoleWrapper(role) for role in self._operation.categories.hive]


class AuthorityRoleWrapper:
    def __init__(self, role: HiveRoleAuthorityDefinition | HiveRoleMemoKeyDefinition) -> None:
        self._role = role

    @property
    def level(self) -> TRole:
        return self._role.level

    @property
    def is_role_memo(self) -> bool:
        return self._role.level == "memo"

    @property
    def value(self) -> AuthorityEntryWrapper | WaxAuthorityWrapper:
        return AuthorityEntryWrapper(self._role.value) if self.is_role_memo else WaxAuthorityWrapper(self._role.value)

    @property
    def is_role_has_entry_that_matches_pattern(self, *patterns: str) -> bool:
        return (
            is_match(self._role.value, *patterns)
            if self.is_role_memo
            else WaxAuthorityWrapper(self._role.value).is_object_has_entry_that_matches_pattern(*patterns)
        )


class WaxAuthorityWrapper:
    """A wrapper to provide utility methods for WaxAuthority objects."""

    def __init__(self, authority: WaxAuthority) -> None:
        self._authority = authority

    @property
    def account_auths(self):
        return [AuthorityEntryWrapper(key_entry, weight) for key_entry, weight in self._authority.account_auths.items()]

    @property
    def key_auths(self):
        return [AuthorityEntryWrapper(key_entry, weight) for key_entry, weight in self._authority.key_auths.items()]

    def collect_all_entries(self) -> list[str]:
        return list(self._authority.account_auths.keys()) + list(self._authority.key_auths.keys())

    def collect_weights(self, keys: KeyManager) -> list[int]:
        """Collect weights for keys that are present in the KeyManager."""
        return [self._authority.key_auths[key] for key in list(self._authority.key_auths.keys()) if key in keys]

    def is_object_has_entry_that_matches_pattern(self, *patterns: str) -> bool:
        return any(is_match(entry, *patterns) for entry in self.collect_all_entries())


class AuthorityEntryWrapper:
    """Wrapper for single authority entry."""

    def __init__(self, key_or_account: str, weight: int | None = None) -> None:
        self._key_or_account = key_or_account
        self._weight = weight

    @property
    def key_or_account(self) -> str:
        return self._key_or_account

    @property
    def weight(self) -> int:
        assert self._weight is not None, "This entry has no weight."
        return self._weight

    @property
    def is_account_entry(self) -> bool:
        return not PublicKey.is_valid(self._key_or_account)
