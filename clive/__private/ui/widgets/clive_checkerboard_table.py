from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Final, Sequence

from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Static

from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from textual.app import ComposeResult


ODD_CLASS_NAME: Final[str] = "-odd-column"
EVEN_CLASS_NAME: Final[str] = "-even-column"


class CliveCheckerboardTableError(CliveError):
    pass


class InvalidDynamicDefinedError(CliveCheckerboardTableError):
    _MESSAGE = """
You are trying to create a dynamic checkerboard table without overriding one of the mandatory properties or methods.
Override it or unset the `ATTRIBUTE_TO_WATCH` class-var  if you want to create a static table.
"""

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


class InvalidStaticDefinedError(CliveCheckerboardTableError):
    _MESSAGE = """
You are trying to create a static checkerboard table without overriding the mandatory `create_static_rows` methods.
Override it or set the `ATTRIBUTE_TO_WATCH` class-var if you want to create a dynamic table.
"""

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


class PlaceTaker(Static):
    pass


class CliveCheckerBoardTableCell(Container):
    """Cell of the checkerboard-table."""

    DEFAULT_CSS = """
    CliveCheckerBoardTableCell {
        height: auto;
        Static {
            text-align: center;
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
    }
    """

    def __init__(self, content: str | Widget, id_: str | None = None, classes: str | None = None) -> None:
        """
        Initialise the checkerboard table cell.

        Args:
        ----
        content: Text to be displayed in the cell or widget to be yielded.
        even: Evenness of the cell.
        id_:  The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        """
        super().__init__(id=id_, classes=classes)
        self._content = content

    def compose(self) -> ComposeResult:
        if isinstance(self._content, Widget):
            yield self._content
        else:
            yield Static(self._content)


class CliveCheckerboardTableRow(CliveWidget):
    """Row with checkerboard columns."""

    DEFAULT_CSS = """
    CliveCheckerboardTableRow {
        layout: horizontal;
        height: auto;
    }
    """

    def __init__(self, *cells: CliveCheckerBoardTableCell):
        super().__init__()
        self.cells = cells

    def compose(self) -> ComposeResult:
        yield from self.cells


class CliveCheckerboardTable(CliveWidget):
    """
    Table that displays checkerboard rows.

    Dynamic usage
    -------------
    1. Change `ATTRIBUTE_TO_WATCH` class-var.
    2. Override `object_to_watch` property.
    3. Override `check_if_should_be_updated`
    4. Override (optionally) `is_anything_to_display`
    5. Override `create_dynamic_rows`

    Static usage
    ------------
    1. Override `create_static_rows`
    """

    DEFAULT_CSS = """
    CliveCheckerboardTable {
        layout: vertical;
        height: auto;

        .-odd-column {
            background: $primary-background-darken-2;

            OneLineButton {
                opacity: 93%;
            }
        }

        .-even-column {
            background: $primary-background-darken-1;
        }

        #loading-static {
            text-align: center;
            text-style: bold;
        }
    }
    """

    ATTRIBUTE_TO_WATCH: ClassVar[str] = ""
    """attribute name to trigger an update of the table and to download new data"""

    def __init__(self, title: Widget, header: Widget):
        super().__init__()
        self._title = title
        self._header = header

    def compose(self) -> ComposeResult:
        if self.should_be_dynamic:
            yield Static("Loading...", id="loading-static")
        else:
            self._mount_static_rows()

    def on_mount(self) -> None:
        if self.should_be_dynamic:
            self.watch(self.object_to_watch, self.ATTRIBUTE_TO_WATCH, self._mount_dynamic_rows)

    def _mount_static_rows(self) -> None:
        """Mount rows created in static mode."""
        rows = self.create_static_rows()
        self._set_evenness_styles(rows)
        self.mount_all([self._title, self._header, *rows])

    async def _mount_dynamic_rows(self, content: Any) -> None:
        """New rows are mounted when the ATTRIBUTE_TO_WATCH has been changed."""
        if not self.should_be_dynamic:
            raise InvalidDynamicDefinedError

        if content is None:  # data not received yet
            return

        if not self.check_if_should_be_updated:
            return

        if self.is_anything_to_display:
            rows = self.create_dynamic_rows(content)
            self._set_evenness_styles(rows)
            widgets_to_mount = [self._title, self._header, *rows]
        else:
            widgets_to_mount = [self.get_no_content_available_widget()]

        with self.app.batch_update():
            await self.query("*").remove()
            await self.mount_all(widgets_to_mount)

    def create_dynamic_rows(self, content: Any) -> Sequence[CliveCheckerboardTableRow]:  # noqa: ARG002
        """
        Override this method when using dynamic table (ATTRIBUTE_TO_WATCH is set).

        Raises
        ------
        InvalidDynamicDefinedError: When ATTRIBUTE_TO_WATCH has been set without overriding the method.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError
        return [CliveCheckerboardTableRow(CliveCheckerBoardTableCell("Define `create_dynamic_rows` method!"))]

    def create_static_rows(self) -> Sequence[CliveCheckerboardTableRow]:
        """
        Override this method when using static table (ATTRIBUTE_TO_WATCH is not set).

        Raises
        ------
        InvalidStaticDefinedError: When ATTRIBUTE_TO_WATCH has not been set without overriding the method.
        """
        if not self.should_be_dynamic:
            raise InvalidStaticDefinedError
        return [CliveCheckerboardTableRow(CliveCheckerBoardTableCell("Define `create_static_rows` method!"))]

    def get_no_content_available_widget(self) -> Widget:
        return Static("No content available")

    @property
    def should_be_dynamic(self) -> bool:
        return bool(self.ATTRIBUTE_TO_WATCH)

    @property
    def check_if_should_be_updated(self) -> bool:
        """
        Must be overridden by the child class when using dynamic table.

        Examples
        --------
        return self.provider.content.actual_value != self.previous_value

        Raises
        ------
        InvalidDynamicDefinedError: When ATTRIBUTE_TO_WATCH has been set without overriding the method.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError
        return True

    def _set_evenness_styles(self, rows: Sequence[CliveCheckerboardTableRow]) -> None:
        for row_index, row in enumerate(rows):
            for cell_index, cell in enumerate(row.cells):
                if not isinstance(cell, CliveCheckerBoardTableCell):
                    continue

                is_even_row = row_index % 2 == 0
                is_even_cell = cell_index % 2 == 0

                if (is_even_row and is_even_cell) or (not is_even_row and not is_even_cell):
                    cell.add_class(EVEN_CLASS_NAME)
                else:
                    cell.add_class(ODD_CLASS_NAME)

    @property
    def object_to_watch(self) -> Any:
        """
        Must be overridden by the child class when using dynamic table.

        Raises
        ------
        InvalidDynamicDefinedError: When ATTRIBUTE_TO_WATCH has been set without overriding the property.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError

    @property
    def is_anything_to_display(self) -> bool:
        """A property that checks whether there are elements to display. Should be overridden to create a custom condition."""
        return True
