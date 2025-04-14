from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.data_providers.abc.data_provider import DataProvider
from clive.__private.ui.not_updated_yet import is_not_updated_yet
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from textual.app import ComposeResult
    from textual.widget import Widget


class CliveDataTableRow(Horizontal, CliveWidget):
    """Class that represent the one line of the clive data table."""

    DEFAULT_CSS = """
    $row-color-odd: $panel-lighten-2;
    $row-color-even: $panel-lighten-3;
    $row-title-color: $primary-lighten-2;

    CliveDataTableRow {
        layout: horizontal;
        width: 1fr;
        height: 1;

        &.-odd {
          background: $row-color-odd;
        }

        &.-even {
          background: $row-color-even;
        }

        RowTitle {
          text-style: bold;
          width: 1fr;
          background: $row-title-color;
          text-align: center;
        }
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

    def refresh_row(self, content: Any) -> None:  # noqa: ANN401
        """Iterate through the cells and update each of them."""
        for cell, value in zip(self.cells, self.get_new_values(content), strict=True):
            cell.update(value)

    def get_new_values(self, content: Any) -> tuple[str, ...]:  # type: ignore[return] # noqa: ARG002, ANN401
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

        self._set_evenness_styles(rows)

    def compose(self) -> ComposeResult:
        yield self._header
        yield from self._rows

    def on_mount(self) -> None:
        if self._dynamic:
            self.watch(self.provider, "_content", self.refresh_rows)

    def refresh_rows(self, content: Any) -> None:  # noqa: ANN401
        if is_not_updated_yet(content):
            return

        with self.app.batch_update():
            for row in self._rows:
                if row._dynamic:
                    row.refresh_row(content)

    def _set_evenness_styles(self, rows: Sequence[CliveDataTableRow]) -> None:
        for row_index, row in enumerate(rows):
            is_even_row = row_index % 2 == 0
            row.add_class("-even" if is_even_row else "-odd")

    @property
    def provider(self) -> DataProvider[Any]:
        return self.screen.query_exactly_one(DataProvider[Any])  # type: ignore[type-abstract]
