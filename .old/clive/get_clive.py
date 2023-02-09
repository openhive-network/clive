from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.app import Clive


def get_clive() -> Clive:
    from clive.app import clive

    return clive
