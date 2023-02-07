from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asyncio import Protocol

    class TableBorderT(Protocol):
        HORIZONTAL: str
        VERTICAL: str

        TOP_LEFT: str
        TOP_RIGHT: str
        BOTTOM_LEFT: str
        BOTTOM_RIGHT: str

        LEFT_T: str
        RIGHT_T: str
        TOP_T: str
        BOTTOM_T: str

        INTERSECT: str


class _SpaceBorder:
    """Box drawing characters. (Spaces)"""

    HORIZONTAL = " "
    VERTICAL = " "

    TOP_LEFT = " "
    TOP_RIGHT = " "
    BOTTOM_LEFT = " "
    BOTTOM_RIGHT = " "

    LEFT_T = " "
    RIGHT_T = " "
    TOP_T = " "
    BOTTOM_T = " "

    INTERSECT = " "


class _AsciiBorder:
    """Box drawing characters. (ASCII)"""

    HORIZONTAL = "-"
    VERTICAL = "|"

    TOP_LEFT = "+"
    TOP_RIGHT = "+"
    BOTTOM_LEFT = "+"
    BOTTOM_RIGHT = "+"

    LEFT_T = "+"
    RIGHT_T = "+"
    TOP_T = "+"
    BOTTOM_T = "+"

    INTERSECT = "+"


class _ThinBorder:
    """Box drawing characters. (Thin)"""

    HORIZONTAL = "\u2500"
    VERTICAL = "\u2502"

    TOP_LEFT = "\u250c"
    TOP_RIGHT = "\u2510"
    BOTTOM_LEFT = "\u2514"
    BOTTOM_RIGHT = "\u2518"

    LEFT_T = "\u251c"
    RIGHT_T = "\u2524"
    TOP_T = "\u252c"
    BOTTOM_T = "\u2534"

    INTERSECT = "\u253c"


class _RoundedBorder(_ThinBorder):
    """Box drawing characters. (Rounded)"""

    TOP_LEFT = "\u256d"
    TOP_RIGHT = "\u256e"
    BOTTOM_LEFT = "\u2570"
    BOTTOM_RIGHT = "\u256f"


class _ThickBorder:
    """Box drawing characters. (Thick)"""

    HORIZONTAL = "\u2501"
    VERTICAL = "\u2503"

    TOP_LEFT = "\u250f"
    TOP_RIGHT = "\u2513"
    BOTTOM_LEFT = "\u2517"
    BOTTOM_RIGHT = "\u251b"

    LEFT_T = "\u2523"
    RIGHT_T = "\u252b"
    TOP_T = "\u2533"
    BOTTOM_T = "\u253b"

    INTERSECT = "\u254b"


class _DoubleBorder:
    """Box drawing characters. (Thin)"""

    HORIZONTAL = "\u2550"
    VERTICAL = "\u2551"

    TOP_LEFT = "\u2554"
    TOP_RIGHT = "\u2557"
    BOTTOM_LEFT = "\u255a"
    BOTTOM_RIGHT = "\u255d"

    LEFT_T = "\u2560"
    RIGHT_T = "\u2563"
    TOP_T = "\u2566"
    BOTTOM_T = "\u2569"

    INTERSECT = "\u256c"


class TableBorder:
    """Border styles for TableContainer."""

    SPACE = _SpaceBorder
    ASCII = _AsciiBorder
    THIN = _ThinBorder
    ROUNDED = _RoundedBorder
    THICK = _ThickBorder
    DOUBLE = _DoubleBorder
