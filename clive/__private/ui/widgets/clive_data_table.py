from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Final

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from typing import ClassVar

    from textual.app import ComposeResult


class CliveDataTableError(Exception):
    """Base exception for all clive data table related exceptions."""


class CellStyleClassesError(CliveDataTableError):
    MESSAGE: Final[str] = """
You are trying to insert too many or too few style classes into table cells.
Remember that you must give one css class per cell, not more or less!
"""

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class CliveTableRowWrapper(Horizontal):
    """Class to create a row with data that will be updated (or not if dynamic is False) in CliveDataTableRow."""

    DEFAULT_CSS = """
    CliveTableRowWrapper .clive-data-table-cell {
        height: 1;
    }
    """

    def __init__(self, content_to_display: list[str], cell_classes: list[str] | None = None):
        """
        Initialize the clive data table row wrapper.

        Args:
        ----
        content_to_display: List of cell contents.
        cell_classes: SCSS style classes for cells.
        """
        super().__init__()
        self._content_to_display = content_to_display
        self._cell_classes = cell_classes

    def compose(self) -> ComposeResult:
        """
        The compose checks the number of SCSS classes and the number of cells - each cell must have a class if given !.

        Raises
        ------
        CellStyleClassesError: When the number of SCSS classes differs from the number of cells.
        """
        if self._cell_classes is None:
            for content in self._content_to_display:
                yield Static(content, classes="clive-data-table-cell")

        else:
            if len(self._cell_classes) != len(self._content_to_display):
                raise CellStyleClassesError

            for style, content in zip(self._cell_classes, self._content_to_display, strict=True):
                yield Static(content, classes=f"clive-data-table-cell {style}")


class CliveDataTableRow(CliveWidget):
    """Class that represent the one line of the clive data table."""

    row_style: ClassVar[str] = "clive-data-table-row"
    """A common css class for all rows. Override it to use yours."""

    DEFAULT_CSS = """
    CliveDataTableRow {
        layout: horizontal;
        width: 1fr;
        height: 1;
    }

    CliveDataTableRow .loading-label {
        text-align: center;
        text-style: bold;
        align: center middle;
    }
    """

    def __init__(self, title_of_row: str, *, dynamic: bool = False, id_: str | None = None) -> None:
        """
        Initialize the clive data table row.

        Args:
        ----
        title_of_row: Title of the row, using to create a SCSS class for the row.
        dynamic: Is dynamic or not.
        id_: The ID of the widget in the DOM.
        """
        self._row_custom_style = f"{title_of_row}-clive-table-row"
        super().__init__(classes=f"{self._row_custom_style} {self.row_style}", id=id_)
        self._is_loading = True
        self._dynamic = dynamic

    def on_mount(self) -> None:
        if self._dynamic:
            self.watch(self.provider, "_content", lambda _: self._sync_row())

    @abstractmethod
    def create_row(self) -> CliveTableRowWrapper | None:
        pass

    async def _sync_row(self) -> None:
        await self.loading_set()

        new_row = self.create_row()
        if new_row is None:
            return

        with self.app.batch_update():
            await self.query("*").remove()
            await self.mount(new_row)

    async def loading_set(self) -> None:
        with self.app.batch_update():
            await self.query("*").remove()
            await self.mount(Static("Loading...", classes="loading-label"))

    @property
    def provider(self) -> Any:
        """Must be overridden if the `dynamic` parameter is set to True."""
        return


class CliveDataTable(CliveWidget):
    """Clive table to show up data that is static or dynamic."""

    DEFAULT_CSS = """
    CliveDataTable {
        layout: vertical;
    }
    """

    table_style: ClassVar[str] = "clive-data-table"
    """A common css class for all clive data tables. Override it to use yours."""
    headline_style: ClassVar[str] = "clive-data-table-header"
    """A common css class for clive data table headers. Override it to use yours."""

    def __init__(self, table_rows: list[CliveDataTableRow], *, id_: str | None = None) -> None:
        """
        Initialize the clive data table.

        Args:
        ----
        table_rows: The rows of the table passed in the list.
        id_: The ID of the widget in the DOM.
        """
        super().__init__(classes=self.table_style, id=id_)
        self._table_rows = table_rows

    def compose(self) -> ComposeResult:
        yield from self.create_table_headlines()
        yield from self._table_rows

    def create_table_headlines(self) -> ComposeResult:
        """A method must be overridden if you want to create the header(s) for the table."""
        return []
