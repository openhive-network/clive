from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


class CliveDataTableError(CliveError):
    """Base class for all clive data table related exceptions."""


class DynamicRowInvalidDefinedError(CliveDataTableError):
    MESSAGE: Final[
        str
    ] = """
You set the `dynamic` parameter to `True` without overriding `sync_row` or `provider` to update the cells.
Override the `sync_row` method or `provider` property or set the `dynamic` parameter to False.
"""

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class CliveDataTableRow(Horizontal, CliveWidget):
    """Class that represent the one line of the clive data table."""

    DEFAULT_CSS = """
    CliveDataTableRow {
        layout: horizontal;
        width: 1fr;
        height: 1;
    }
    """

    def __init__(
        self,
        title: str,
        *cells: Static,
        dynamic: bool = False,
        classes: str | None = None,
        id_: str | None = None,
    ) -> None:
        """
        Initialize the clive data table row.

        Args:
        ----
        title: Title of the row. Will be displayed as the first cell.
        cells: Cells of the table as Static/Label widgets.
        dynamic: Is dynamic or not.
        classes: The CSS classes for the widget.
        id_: The ID of the widget in the DOM.
        """
        super().__init__(classes=classes, id=id_)
        self._dynamic = dynamic
        self._row_title = title

        self.cells = cells
        """Attribute that holds cells to modify in `sync_rows` method"""

    class RowTitle(Static):
        """Title of the table row."""

    def on_mount(self) -> None:
        if self._dynamic:
            self.watch(self.provider, "_content", self._update_row, init=False)

    def compose(self) -> ComposeResult:
        yield self.RowTitle(self._row_title)
        yield from self.cells

    def _update_row(self, content: Any) -> None:
        """Iterate through the cells and update each of them."""
        for cell, balance in zip(self.cells, self.get_new_values(content), strict=True):
            cell.update(balance)

    def get_new_values(self, content: Any) -> tuple[str, ...]:  # type: ignore[return] # noqa: ARG002
        """
        Must be overridden if the `dynamic` parameter is set to True.

        Raises
        ------
        DynamicRowInvalidDefinedError: Raised when `dynamic` is set to True without overriding this method.
        """
        if self._dynamic:
            raise DynamicRowInvalidDefinedError

    @property
    def provider(self) -> Any:
        """
        Must be overridden if the `dynamic` parameter is set to True.

        Raises
        ------
        DynamicRowInvalidDefinedError: Raised when `dynamic` is set to True without overriding this method.
        """
        if self._dynamic:
            raise DynamicRowInvalidDefinedError


class CliveDataTable(CliveWidget):
    """Clive table to show up data that is static or dynamic."""

    DEFAULT_CSS = """
    CliveDataTable {
        layout: vertical;
    }
    """

    def __init__(
        self, header: Widget, *rows: CliveDataTableRow, classes: str | None = None, id_: str | None = None
    ) -> None:
        """
        Initialize the clive data table.

        Args:
        ----
        header: The headline of the table.
        rows: The rows of the table.
        classes: The CSS classes for the widget.
        id_: The ID of the widget in the DOM.
        """
        super().__init__(classes=classes, id=id_)
        self._table_headline = header
        self._table_rows = rows

    def compose(self) -> ComposeResult:
        yield self._table_headline
        yield from self._table_rows
