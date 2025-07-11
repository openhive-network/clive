from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.ui.app import Clive


def get_clive() -> type[Clive]:
    """
    Get the Clive class. Helper function useful when circular imports occurs.

    Returns:
        The Clive class.
    """
    from clive.__private.ui.app import Clive

    return Clive
