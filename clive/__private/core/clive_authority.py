from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal

from clive.__private.core.keys.keys import PublicKey
from clive.__private.core.str_utils import is_match
from wax.models.authority import WaxAuthority

if TYPE_CHECKING:
    from clive.__private.core.keys.key_manager import KeyManager
    from wax.complex_operations.account_update import AccountAuthorityUpdateOperation
    from wax.complex_operations.role_classes.hive_authority.hive_role_authority_definition import (
        HiveRoleAuthorityDefinition,
    )
    from wax.complex_operations.role_classes.hive_authority.hive_role_memo_key import HiveRoleMemoKeyDefinition
    from wax.complex_operations.role_classes.hive_authority.hive_roles import (
        ActiveRoleName,
        OwnerRoleName,
        PostingRoleName,
    )


class CliveAuthority:
    """
    Wrapper for account authority update operation from wax.

    Args:
        operation: The account authority update operation to wrap.
    """

    def __init__(self, operation: AccountAuthorityUpdateOperation) -> None:
        self._operation = operation

    @property
    def account(self) -> str:
        return self._operation.categories.hive.account

    @property
    def active(self) -> CliveAuthorityRoleWrapper:
        return CliveAuthorityRoleWrapper(self._operation.roles.active)

    @property
    def memo(self) -> CliveAuthorityRoleWrapper:
        return CliveAuthorityRoleWrapper(self._operation.roles.memo)

    @property
    def owner(self) -> CliveAuthorityRoleWrapper:
        return CliveAuthorityRoleWrapper(self._operation.roles.owner)

    @property
    def posting(self) -> CliveAuthorityRoleWrapper:
        return CliveAuthorityRoleWrapper(self._operation.roles.posting)

    @property
    def roles(self) -> list[CliveAuthorityRoleWrapper]:
        return [self.active, self.owner, self.posting, self.memo]

    def get(self) -> list[CliveAuthorityEntryWrapper]:
        """
        Return all authority entry wrapper objects inside this authority.

        Returns:
            All authority entry wrapper objects inside this authority.
        """
        return [entry for role in self.roles for entry in role.get()]


class CliveAuthorityRoleWrapper:
    """
    Wrapper for hive role authority definitions to provide utility methods.

    Args:
        role: Role to wrap.
    """

    def __init__(
        self,
        role: HiveRoleAuthorityDefinition[ActiveRoleName]
        | HiveRoleAuthorityDefinition[OwnerRoleName]
        | HiveRoleAuthorityDefinition[PostingRoleName]
        | HiveRoleMemoKeyDefinition,
    ) -> None:
        self._role = role

    @property
    def level(self) -> Literal["memo", "active", "owner", "posting"]:
        return self._role.level

    @property
    def is_role_memo(self) -> bool:
        return self._role.level == "memo"

    @property
    def value(self) -> CliveAuthorityEntryWrapper | CliveAuthorityWrapper:
        value = self._role.value
        if isinstance(value, WaxAuthority) and not self.is_role_memo:
            return CliveAuthorityWrapper(value)
        return CliveAuthorityEntryWrapper(value)

    def get(self) -> list[CliveAuthorityEntryWrapper]:
        return self.value.get()

    def is_role_has_entry_that_matches_pattern(self, *patterns: str) -> bool:
        return self.value.is_match(*patterns)


class CliveAuthorityBase(ABC):
    """Abstract base class for clive authority wrapper and clive authority entry wrapper."""

    @property
    @abstractmethod
    def is_memo_authority(self) -> bool:
        pass

    @abstractmethod
    def is_match(self, *patterns: str) -> bool:
        pass

    @abstractmethod
    def get(self) -> list[CliveAuthorityEntryWrapper]:
        pass


class CliveAuthorityWrapper(CliveAuthorityBase):
    """
    A wrapper to provide utility methods for wax authority objects.

    Args:
        authority: Wax authority object to wrap.
    """

    def __init__(self, authority: WaxAuthority) -> None:
        super().__init__()
        self._authority = authority

    @property
    def account_auths(self) -> list[CliveAuthorityEntryWrapper]:
        return [
            CliveAuthorityEntryWrapper(key_entry, weight) for key_entry, weight in self._authority.account_auths.items()
        ]

    @property
    def key_auths(self) -> list[CliveAuthorityEntryWrapper]:
        return [
            CliveAuthorityEntryWrapper(key_entry, weight) for key_entry, weight in self._authority.key_auths.items()
        ]

    @property
    def all_auths(self) -> list[CliveAuthorityEntryWrapper]:
        """Get all wrapped authority entries (keys and accounts)."""
        return self.account_auths + self.key_auths

    @property
    def is_memo_authority(self) -> bool:
        return False

    @property
    def weight_threshold(self) -> int:
        return self._authority.weight_threshold

    def get(self) -> list[CliveAuthorityEntryWrapper]:
        return self.all_auths

    def is_match(self, *patterns: str) -> bool:
        """
        Checks is any entry matches given pattern.

        Args:
            *patterns: Patterns to match against authority entries.

        Returns:
            True if any entry matches the pattern, False otherwise.
        """
        return any(entry_wrapper_object.is_match(*patterns) for entry_wrapper_object in self.all_auths)

    def collect_all_entries(self) -> list[str]:
        return list(self._authority.account_auths.keys()) + list(self._authority.key_auths.keys())

    def collect_weights(self, keys: KeyManager) -> list[int]:
        """
        Collect weights for keys that are present in the key manager.

        Args:
            keys: Key manager instance to check against.

        Returns:
            List of weights for keys that are present in the key manager and this wrapper object.

        """
        return [self._authority.key_auths[key] for key in list(self._authority.key_auths.keys()) if key in keys]


class CliveAuthorityEntryWrapper(CliveAuthorityBase):
    """
    Wrapper for single authority entry.

    Args:
        key_or_account: Key or account name of the authority entry.
        weight: Weight of the authority entry if it is a key entry.
    """

    def __init__(self, key_or_account: str, weight: int | None = None) -> None:
        super().__init__()
        self._key_or_account = key_or_account
        self._weight = weight

    @property
    def key_or_account(self) -> str:
        return self._key_or_account

    @property
    def weight(self) -> int | None:
        return self._weight

    @property
    def is_account_entry(self) -> bool:
        return not PublicKey.is_valid(self._key_or_account)

    @property
    def is_memo_authority(self) -> bool:
        return not self.is_account_entry and self._weight is None

    @property
    def public_key(self) -> PublicKey:
        assert not self.is_account_entry, "This property is only available for key entries."
        return PublicKey(value=self._key_or_account)

    def get(self) -> list[CliveAuthorityEntryWrapper]:
        return [self]

    def is_match(self, *patterns: str) -> bool:
        return is_match(self._key_or_account, *patterns)
