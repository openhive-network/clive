from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.containers import Horizontal

from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult

ODD_STYLE: Final[str] = "OddColumn"
EVEN_STYLE: Final[str] = "EvenColumn"


class CliveCheckerboardTableRow(CliveWidget):
    """Class with checkerboard columns, use `ODD_STYLE` and `EVEN_STYLE` to achieve the desired effect."""

    DEFAULT_CSS = """
    CliveCheckerboardTableRow {
        layout: horizontal;
    }
    """

    def compose(self) -> ComposeResult:
        yield from self.create_row_columns()

    def create_row_columns(self) -> ComposeResult:
        return []


class CliveCheckerboardTable(CliveWidget):
    DEFAULT_CSS = """
    CliveCheckerboardTable {
        layout: vertical;
    }

    CliveCheckerboardTable .OddColumn {
        background: $primary-background-darken-2;
    }

    CliveCheckerboardTable .EvenColumn {
        background: $primary-background-darken-1;
    }
    """

    def compose(self) -> ComposeResult:
        yield from self.create_table_title()
        with Horizontal(classes="checkerboard-table-header"):
            yield from self.create_header_columns()
        yield from self.create_rows()

    def create_header_columns(self) -> ComposeResult:
        return []

    def create_table_title(self) -> ComposeResult:
        return []

    def create_rows(self) -> ComposeResult:
        """The method must yield the `CliveCheckerboardTableRow` class to achieve the checkerboard effect."""
        return []
