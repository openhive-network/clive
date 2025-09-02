from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from clive.__private.core.clive_authority.entries import CliveAuthorityEntryBase


class CliveAuthorityEntriesHolder(ABC):
    @abstractmethod
    def get_entries(self) -> Sequence[CliveAuthorityEntryBase]:
        """
        Return all authority entry wrapper objects inside this authority.

        Returns:
           All authority entry wrapper objects inside this authority.
        """
