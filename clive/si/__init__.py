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

    # Basic transfer - ALWAYS use async with
    async with clive_use_unlocked_profile() as clive:
        await clive.process.transfer(
            from_account="alice",
            to_account="bob",
            amount="1.000 HIVE",
            memo="Payment"
        ).broadcast()

    # Or directly - ALWAYS use async with
    async with UnlockedCliveSi() as clive:
        await clive.process.transfer(
            from_account="alice",
            to_account="bob",
            amount="1.000 HIVE",
        ).broadcast()

    # Multiple operations in one transaction
    async with clive_use_unlocked_profile() as clive:
        await clive.process.transfer(
            from_account="alice",
            to_account="bob",
            amount="1.000 HIVE",
        ).process.transfer(
            from_account="alice",
            to_account="charlie",
            amount="2.000 HIVE",
        ).sign_with("5J...").broadcast()

    # Query operations (no profile needed) - ALSO use async with
    async with CliveSi() as clive:
        profiles = await clive.show.profiles()
    ```
"""

from __future__ import annotations

from clive.__private.si.base import CliveSi, UnlockedCliveSi, clive_use_unlocked_profile

__all__ = [
    "CliveSi",
    "UnlockedCliveSi",
    "clive_use_unlocked_profile",
]
