"""Authority modification operations for ProcessAuthority - delegates to shared core operations."""

from __future__ import annotations

# Re-export all functions from the shared core module
from clive.__private.core.operations.authority_operations import (
    AuthorityAlreadyExistsError,
    AuthorityNotFoundError,
    add_account,
    add_key,
    build_account_update_operation,
    is_on_auths_list,
    modify_account,
    modify_key,
    remove_account,
    remove_key,
    set_threshold,
)

__all__ = [
    "AuthorityAlreadyExistsError",
    "AuthorityNotFoundError",
    "add_account",
    "add_key",
    "build_account_update_operation",
    "is_on_auths_list",
    "modify_account",
    "modify_key",
    "remove_account",
    "remove_key",
    "set_threshold",
]
