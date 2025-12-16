"""
Clive Python Interface (PY).

This module provides a programmatic interface for interacting with Clive functionality.
It allows developers to write Python scripts that perform blockchain operations.

Main classes:
    ClivePy - Interface for read-only operations (no profile needed)
    UnlockedClivePy - Full interface with unlocked profile for all operations

Factory function:
    clive_use_unlocked_profile() - Convenient way to get UnlockedClivePy instance

IMPORTANT: UnlockedClivePy and clive_use_unlocked_profile() MUST be used as async context managers.
The context manager handles:
- Profile loading from the unlocked beekeeper wallet on entry
- Profile saving to storage on exit
- Proper cleanup of all resources

Example usage:
    ```python
    from clive.py import ClivePy, UnlockedClivePy, clive_use_unlocked_profile

    # Query profiles (no profile needed)
    async with ClivePy() as clive:
        profiles = await clive.show.profiles()

    # Operations with profile - ALWAYS use async with
    async with clive_use_unlocked_profile() as clive:
        # Show operations
        balances = await clive.show.balances("alice")
        accounts = await clive.show.accounts()
        witnesses = await clive.show.witnesses("alice", page_size=30, page_no=0)
        owner_auth = await clive.show.owner_authority("alice")
        active_auth = await clive.show.active_authority("alice")
        posting_auth = await clive.show.posting_authority("alice")

    # Or directly - ALWAYS use async with
    async with UnlockedClivePy() as clive:
        balances = await clive.show.balances("bob")
    ```

Note: Process operations (transfer, update_authority, etc.) will be available in a future release.
"""

from __future__ import annotations

from clive.__private.py.base import ClivePy, UnlockedClivePy, clive_use_unlocked_profile

__all__ = [
    "ClivePy",
    "UnlockedClivePy",
    "clive_use_unlocked_profile",
]
