from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from clive.__private.core.authority.entries import AuthorityEntryBase


class AuthorityEntriesHolder(ABC):
    """An abstract base class for objects that are able to extract authority entries from themselves."""

    @abstractmethod
    def get_entries(self) -> Sequence[AuthorityEntryBase]:
        """
        Get all authority entry objects provided by this holder.

        Returns:
            A sequence of authority entry objects.
        """
