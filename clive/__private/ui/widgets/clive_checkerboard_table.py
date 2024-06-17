from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Final, Sequence, TypeVar

from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Static

from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.exceptions import CliveDeveloperError

if TYPE_CHECKING:
    from textual.app import ComposeResult


ODD_CLASS_NAME: Final[str] = "-odd-column"
EVEN_CLASS_NAME: Final[str] = "-even-column"

Content = TypeVar("Content", bound=Any)


class CliveCheckerboardTableError(CliveDeveloperError):
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


class RebuildStaticTableWithContentError(CliveCheckerboardTableError):
    _MESSAGE = "Cannot rebuild static table with content param given. Maybe you should use dynamic table?"

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


class PlaceTaker(Static):
    pass


class CliveCheckerBoardTableCell(Container):
    """Cell of the checkerboard-table."""

    DEFAULT_CSS = """
    CliveCheckerBoardTableCell {
        height: 1;

        Static {
            width: 1fr;
            height: 1fr;
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

    def __init__(self, *cells: CliveCheckerBoardTableCell) -> None:
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
    6. Override `update_previous_state` (with creating your own previous state in the `__init__` method).

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

    def __init__(self, title: Widget, header: Widget) -> None:
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

            def delegate_work(content: Content) -> None:
                self.run_worker(self._mount_dynamic_rows(content))

            self.watch(self.object_to_watch, self.ATTRIBUTE_TO_WATCH, delegate_work)

    def _mount_static_rows(self) -> None:
        """Mount rows created in static mode."""
        self.mount_all(self._create_table_content())

    async def _mount_dynamic_rows(self, content: Content) -> None:
        """Mount new rows when the ATTRIBUTE_TO_WATCH has been changed."""
        if not self.should_be_dynamic:
            raise InvalidDynamicDefinedError

        if content is None:  # data not received yet
            return

        if not self.check_if_should_be_updated(content):
            return

        self.update_previous_state(content)
        await self.rebuild(content)

    async def rebuild(self, content: Content | None = None) -> None:
        """
        Rebuilds whole table - explicit use available for static and dynamic version.

        Raises
        ------
        RebuildStaticTableWithContentError: When table is static and content arg is provided.
        """
        if not self.should_be_dynamic and content is not None:  # content is given, but table is static
            raise RebuildStaticTableWithContentError

        with self.app.batch_update():
            await self.query("*").remove()
            await self.mount_all(self._create_table_content(content))

    def _create_table_content(self, content: Content | None = None) -> list[Widget]:
        if content is not None and not self.is_anything_to_display(
            content
        ):  # if content is given, we can check if there is anything to display and return earlier
            return [self.get_no_content_available_widget()]

        if self.should_be_dynamic:
            assert content is not None, "Content must be provided when creating dynamic rows."
            rows = self.create_dynamic_rows(content)
        else:
            rows = self.create_static_rows()

        self._set_evenness_styles(rows)
        return [self._title, self._header, *rows]

    def create_dynamic_rows(self, content: Content) -> Sequence[CliveCheckerboardTableRow]:  # noqa: ARG002
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

    def check_if_should_be_updated(self, content: Content) -> bool:  # noqa: ARG002
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

    def is_anything_to_display(self, content: Content) -> bool:  # noqa: ARG002
        """Check whether there are elements to display. Should be overridden to create a custom condition."""
        return True

    def update_previous_state(self, content: Content) -> None:  # noqa: ARG002
        """
        Must be overridden if the `ATTRIBUTE_TO_WATCH` class-var is set.

        Notice that you must also create your own previous state in the `__init__` method.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError
