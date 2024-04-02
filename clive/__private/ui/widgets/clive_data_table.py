from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.ui.data_providers.abc.data_provider import DataProvider
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


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
        dynamic: Whether it should be updated dynamically.
        classes: The CSS classes for the widget.
        id_: The ID of the widget in the DOM.
        """
        super().__init__(classes=classes, id=id_)
        self._dynamic = dynamic
        self._title = title
        self.cells = cells

    class RowTitle(Static):
        """Title of the table row."""

    def compose(self) -> ComposeResult:
        yield self.RowTitle(self._title)
        yield from self.cells

    def refresh_row(self, content: Any) -> None:
        """Iterate through the cells and update each of them."""
        if content is None:  # data not received yet
            return

        for cell, value in zip(self.cells, self.get_new_values(content), strict=True):
            cell.update(value)

    def get_new_values(self, content: Any) -> tuple[str, ...]:  # type: ignore[return] # noqa: ARG002
        """Must be overridden if the `dynamic` parameter is set to True."""
        if self._dynamic:
            raise CliveError("You must override this method if the row is dynamic.")


class CliveDataTable(CliveWidget):
    """Clive table to show up data that is static or dynamic."""

    DEFAULT_CSS = """
    CliveDataTable {
        layout: vertical;
    }
    """

    def __init__(
        self,
        header: Widget,
        *rows: CliveDataTableRow,
        dynamic: bool = False,
        classes: str | None = None,
        id_: str | None = None,
    ) -> None:
        """
        Initialize the clive data table.

        Args:
        ----
        header: The headline of the table.
        rows: The rows of the table.
        dynamic: Whether the table should be updated dynamically (has at least 1 dynamic row).
        classes: The CSS classes for the widget.
        id_: The ID of the widget in the DOM.
        """
        super().__init__(classes=classes, id=id_)
        self._header = header
        self._rows = rows
        self._dynamic = dynamic

    def compose(self) -> ComposeResult:
        yield self._header
        yield from self._rows

    def on_mount(self) -> None:
        if self._dynamic:
            self.watch(self.provider, "_content", self.refresh_rows)

    def refresh_rows(self, content: Any) -> None:
        if content is None:  # data not received yet
            return

        with self.app.batch_update():
            for row in self._rows:
                if row._dynamic:
                    row.refresh_row(content)

    @property
    def provider(self) -> DataProvider[Any]:
        return self.screen.query_one(DataProvider[Any])  # type: ignore[type-abstract]
