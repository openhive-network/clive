"""
Clive Script Interface (SI).

This module provides a programmatic interface for interacting with Clive functionality.
It allows developers to write Python scripts that perform blockchain operations.

Main classes:
    CliveSi - Interface for read-only operations (no profile needed)
    UnlockedCliveSi - Full interface with unlocked profile for all operations

Factory function:
    clive_use_unlocked_profile() - Convenient way to get UnlockedCliveSi instance

IMPORTANT: UnlockedCliveSi and clive_use_unlocked_profile() MUST be used as async context managers.
The context manager handles:
- Profile loading from the unlocked beekeeper wallet on entry
- Profile saving to storage on exit
- Proper cleanup of all resources

Example usage:
    ```python
    from clive.si import CliveSi, UnlockedCliveSi, clive_use_unlocked_profile

    # Query profiles (no profile needed)
    async with CliveSi() as clive:
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
    async with UnlockedCliveSi() as clive:
        balances = await clive.show.balances("bob")
    ```

Note: Process operations (transfer, update_authority, etc.) will be available in a future release.
"""

from __future__ import annotations

from clive.__private.si.base import CliveSi, UnlockedCliveSi, clive_use_unlocked_profile

__all__ = [
    "CliveSi",
    "UnlockedCliveSi",
    "clive_use_unlocked_profile",
]
