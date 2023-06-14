from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.ui.app import Clive


def get_clive() -> type[Clive]:
    """Helper function to get the Clive class. Useful when circular imports occurs."""
    from clive.__private.ui.app import Clive

    return Clive
