from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Static

from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.not_updated_yet import NotUpdatedYet, is_not_updated_yet, is_updated
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.section_title import SectionTitle
from clive.exceptions import CliveDeveloperError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from textual.app import ComposeResult
    from textual.visual import VisualType

ContentT = TypeVar("ContentT", bound=Any)

type CellContent = "VisualType | Widget"


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

    def __init__(self, content: CellContent, id_: str | None = None, classes: str | None = None) -> None:
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

    @property
    def content(self) -> CellContent:
        return self._content

    def compose(self) -> ComposeResult:
        if isinstance(self._content, Widget):
            yield self._content
        else:
            yield Static(self._content)

    async def update_content(self, content: CellContent) -> None:
        self._content = content
        await self.recompose()


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
            background: $panel-lighten-2;

            OneLineButton {
                opacity: 93%;
            }
        }

        .-even-column {
            background: $panel-lighten-1;
        }

        #loading-static {
            text-align: center;
            text-style: bold;
        }

        .checkerboard-header-cell {
            background: $primary;
        }

        .checkerboard-table-title {
            background: $primary-darken-3;
        }
    }
    """

    ATTRIBUTE_TO_WATCH: ClassVar[str] = ""
    """attribute name to trigger an update of the table and to download new data"""
    NO_CONTENT_TEXT: ClassVar[str] = "No content available"

    def __init__(self, *, header: Widget, title: str | Widget | None = None, init_dynamic: bool = True) -> None:
        """
        Initialise the checkerboard table.

        Args:
        ----
        header: Header of the table.
        title: Title of the table.
        init_dynamic: Whether the table should be created right away because data is already available.
            If not set will display "Loading..." until the data is received.
        """
        super().__init__()
        self._title = title
        self._header = header
        self._init_dynamic = init_dynamic

    def compose(self) -> ComposeResult:
        if not self.should_be_dynamic:
            yield from self._create_table_content()
            return

        if self.should_be_dynamic and not self._init_dynamic:
            yield Static("Loading...", id="loading-static")
            return

        content = self._get_dynamic_initial_content()
        if is_updated(content):
            self.update_previous_state(content)
        yield from self._create_table_content(content)

    def on_mount(self) -> None:
        if self.should_be_dynamic:
            self.watch(
                self.object_to_watch, self.ATTRIBUTE_TO_WATCH, self._update_dynamic_table, init=not self._init_dynamic
            )

    async def _update_dynamic_table(self, content: ContentT) -> None:
        if not self.should_be_dynamic:
            raise InvalidDynamicDefinedError

        if is_not_updated_yet(content):
            return

        if not self.check_if_should_be_updated(content):
            return

        self.update_previous_state(content)
        await self.rebuild(content)

    async def rebuild(self, content: ContentT | NotUpdatedYet | None = None) -> None:
        """Rebuilds whole table - explicit use available for static and dynamic version."""
        with self.app.batch_update():
            await self.query("*").remove()
            await self.mount_all(self._create_table_content(content))

    async def rebuild_rows(self, content: ContentT | NotUpdatedYet | None = None) -> None:
        """Rebuilds table rows - explicit use available for static and dynamic version."""
        with self.app.batch_update():
            await self.query(CliveCheckerboardTableRow).remove()

            new_rows = self._create_table_rows(content)
            await self.mount_all(new_rows)

    def _get_dynamic_initial_content(self) -> object:
        return getattr(self.object_to_watch, self.ATTRIBUTE_TO_WATCH)

    def _create_table_rows(
        self, content: ContentT | NotUpdatedYet | None = None
    ) -> Sequence[CliveCheckerboardTableRow]:
        if content is not None and is_updated(content) and not self.is_anything_to_display(content):
            # if content is given, we can check if there is anything to display and return earlier
            return []

        if self.should_be_dynamic:
            assert content is not None, (
                "Content must be provided when creating dynamic rows. Maybe you should use static table?"
            )

            if is_not_updated_yet(content):
                return []

            rows = self.create_dynamic_rows(content)
        else:
            assert content is None, (
                "Content must not be provided when creating static rows. Maybe you should use dynamic table?"
            )
            rows = self.create_static_rows()

        self._set_evenness_styles(rows)
        return rows

    def _create_table_content(self, content: ContentT | NotUpdatedYet | None = None) -> list[Widget]:
        rows = self._create_table_rows(content)

        if not rows:
            return [self._get_no_content_available_widget()]

        if self._title is None:
            return [self._header, *rows]

        title = self._title if isinstance(self._title, Widget) else SectionTitle(self._title)
        return [title, self._header, *rows]

    def create_dynamic_rows(self, content: ContentT) -> Sequence[CliveCheckerboardTableRow]:  # noqa: ARG002
        """
        Override this method when using dynamic table (ATTRIBUTE_TO_WATCH is set).

        Raises:  # noqa: D406
        ------
        InvalidDynamicDefinedError: When ATTRIBUTE_TO_WATCH has been set without overriding the method.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError
        return []

    def create_static_rows(self) -> Sequence[CliveCheckerboardTableRow]:
        """
        Override this method when using static table (ATTRIBUTE_TO_WATCH is not set).

        Raises:  # noqa: D406
        ------
        InvalidStaticDefinedError: When ATTRIBUTE_TO_WATCH has not been set without overriding the method.
        """
        if not self.should_be_dynamic:
            raise InvalidStaticDefinedError
        return []

    def _get_no_content_available_widget(self) -> Widget:
        return CliveCheckerboardTableRow(CliveCheckerBoardTableCell(NoContentAvailable(self.NO_CONTENT_TEXT)))

    @property
    def should_be_dynamic(self) -> bool:
        return bool(self.ATTRIBUTE_TO_WATCH)

    def check_if_should_be_updated(self, content: ContentT) -> bool:  # noqa: ARG002
        """
        Must be overridden by the child class when using dynamic table.

        Examples:
        --------
        return self.provider.content.actual_value != self.previous_value

        Raises:  # noqa: D406
        ------
        InvalidDynamicDefinedError: When ATTRIBUTE_TO_WATCH has been set without overriding the method.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError
        return True

    def _set_evenness_styles(self, rows: Sequence[CliveCheckerboardTableRow], starting_index: int = 0) -> None:
        for row_index, row in enumerate(rows):
            for cell_index, cell in enumerate(row.cells):
                if not isinstance(cell, CliveCheckerBoardTableCell):
                    continue

                is_even_row = (row_index + starting_index) % 2 == 0
                is_even_cell = cell_index % 2 == 0

                cell.remove_class(CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME)

                if (is_even_row and is_even_cell) or (not is_even_row and not is_even_cell):
                    cell.add_class(CLIVE_EVEN_COLUMN_CLASS_NAME)
                else:
                    cell.add_class(CLIVE_ODD_COLUMN_CLASS_NAME)

    @property
    def object_to_watch(self) -> Any:  # noqa: ANN401
        """
        Must be overridden by the child class when using dynamic table.

        Raises:  # noqa: D406
        ------
        InvalidDynamicDefinedError: When ATTRIBUTE_TO_WATCH has been set without overriding the property.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError

    def is_anything_to_display(self, content: ContentT) -> bool:  # noqa: ARG002
        """Check whether there are elements to display. Should be overridden to create a custom condition."""
        return True

    def update_previous_state(self, content: ContentT) -> None:  # noqa: ARG002
        """
        Must be overridden if the `ATTRIBUTE_TO_WATCH` class-var is set.

        Notice that you must also create your own previous state in the `__init__` method.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError
