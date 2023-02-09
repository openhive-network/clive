from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.ui.clive import Clive


def get_clive() -> Clive:
    from clive.ui.clive import clive

    return clive
