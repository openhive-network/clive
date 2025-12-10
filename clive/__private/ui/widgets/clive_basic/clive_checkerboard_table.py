from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self, TypeVar

from textual import on
from textual.binding import Binding
from textual.containers import Container
from textual.css.query import NoMatches
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.core.constants.tui.texts import LOADING_TEXT
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.not_updated_yet import NotUpdatedYet, is_not_updated_yet, is_updated
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.section_title import SectionTitle
from clive.exceptions import CliveDeveloperError

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

    from textual.app import ComposeResult
    from textual.css.query import DOMQuery
    from textual.visual import VisualType

    from clive.__private.core.str_utils import Matchable

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
    """
    Cell of the checkerboard-table.

    Attributes:
        DEFAULT_CSS: Default CSS for the cell.

    Args:
        content: Text to be displayed in the cell or widget to be yielded.
        id_: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
    """

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
    """
    Row with checkerboard columns.

    Attributes:
        BINDINGS: Key bindings for row.

    Args:
        *cells: Cells to mount in row.
    """

    DEFAULT_CSS = """
    CliveCheckerboardTableRow {
        layout: horizontal;
        height: auto;

        &:focus-within > * {
            background-tint: $foreground 20%;
        }
    }
    """

    BINDINGS = [
        Binding("left", "focus_previous_widget_within_row", "Focus previous widget within row", show=False),
        Binding("right", "focus_next_widget_within_row", "Focus next widget within row", show=False),
        Binding("up", "focus_previous_row", "Focus previous row", show=False),
        Binding("down", "focus_next_row", "Focus next row", show=False),
    ]

    @dataclass
    class FocusOtherRow(Message):
        """
        Message sent when other row should be focused.

        Attributes:
            target_index: Index of row that is about to be focused.
        """

        target_index: int

    def __init__(self, *cells: CliveCheckerBoardTableCell) -> None:
        super().__init__()
        self._index: int | None = None
        self.cells = cells

    @property
    def index(self) -> int:
        assert self._index is not None, (
            "Index is not available yet. Will be available after rows creation in the table."
        )
        return self._index

    @property
    def focusable_children(self) -> list[Widget]:
        return [widget for widget in self.query("*") if widget.focusable]

    def compose(self) -> ComposeResult:
        yield from self.cells

    def action_focus_next_row(self) -> None:
        self.post_message(self.FocusOtherRow(self.index + 1))

    def action_focus_previous_row(self) -> None:
        self.post_message(self.FocusOtherRow(self.index - 1))

    def action_focus_next_widget_within_row(self) -> None:
        self.focus_child(direction="next")

    def action_focus_previous_widget_within_row(self) -> None:
        self.focus_child(direction="previous")

    def focus(self, _: bool = True) -> Self:  # noqa: FBT001, FBT002
        def focus_nth_focusable(*, index: int = 0) -> None:
            focusable_children = self.focusable_children
            if index < len(focusable_children):
                focusable_children[index].focus()

        previously_focused = self.app.focused
        if not previously_focused:
            focus_nth_focusable()
            return self

        try:
            child_with_same_type_as_before = self.query_exactly_one(type(previously_focused))
        except NoMatches:
            focus_nth_focusable()
            return self

        if child_with_same_type_as_before.focusable:
            child_with_same_type_as_before.focus()
        else:
            focus_nth_focusable(index=1)
        return self

    def focus_child(self, direction: Literal["next", "previous"]) -> None:
        currently_focused = self.app.focused
        if not currently_focused:
            # No currently focused widget; do nothing
            return

        focusable_children = self.focusable_children
        try:
            current_index = focusable_children.index(currently_focused)
        except ValueError:
            # Current focus is not my child or have no focusable children; do nothing
            return

        step = 1 if direction == "next" else -1
        target_index = (current_index + step) % len(focusable_children)
        focusable_children[target_index].focus()

    def humanize_row_number(self) -> str:
        return str(self.index + 1)


class CliveCheckerboardTable(CliveWidget):
    """
    Table that displays checkerboard rows.

    Dynamic usage:
        1. Change `ATTRIBUTE_TO_WATCH` class-var.
        2. Override `object_to_watch` property.
        3. Override `check_if_should_be_updated`
        4. Override (optionally) `is_anything_to_display`
        5. Override `create_dynamic_rows`
        6. Override `update_previous_state` (with creating your own previous state in the `__init__` method).

    Static usage:
        1. Override `create_static_rows`

    Attributes:
        DEFAULT_CSS: Default CSS for the table.
        ATTRIBUTE_TO_WATCH: Name of the attribute to observe for triggering table updates in dynamic mode.
        NO_CONTENT_TEXT: Text to display when the table has no content available.

    Args:
        header: Header of the table.
        title: Title of the table.
        init_dynamic: Whether the table should be created right away because data is already available.
            If not set will display loading text until the data is received.
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
    NO_CONTENT_TEXT: ClassVar[str] = "No content available"

    def __init__(self, *, header: Widget, title: str | Widget | None = None, init_dynamic: bool = True) -> None:
        super().__init__()
        self._title = title
        self._header = header
        self._init_dynamic = init_dynamic

    @property
    def should_be_dynamic(self) -> bool:
        return bool(self.ATTRIBUTE_TO_WATCH)

    @property
    def object_to_watch(self) -> Any:  # noqa: ANN401
        """
        Must be overridden by the child class when using dynamic table.

        Raises:
            InvalidDynamicDefinedError: When ATTRIBUTE_TO_WATCH has been set without overriding the property.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError

    @property
    def rows(self) -> DOMQuery[CliveCheckerboardTableRow]:
        return self.query(CliveCheckerboardTableRow)

    def compose(self) -> ComposeResult:
        if not self.should_be_dynamic:
            yield from self._create_table_content()
            return

        if self.should_be_dynamic and not self._init_dynamic:
            yield Static(LOADING_TEXT.capitalize(), id="loading-static")
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

    @on(CliveCheckerboardTableRow.FocusOtherRow)
    def focus_other_row(self, event: CliveCheckerboardTableRow.FocusOtherRow) -> None:
        rows = self.rows
        target_index = event.target_index % len(rows)
        for row in rows:
            if target_index == row._index:
                row.focus()

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

        # auto index given rows
        for index, row in enumerate(rows):
            row._index = index

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

        Raises:
            InvalidDynamicDefinedError: When ATTRIBUTE_TO_WATCH has been set without overriding the method.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError
        return []

    def create_static_rows(self) -> Sequence[CliveCheckerboardTableRow]:
        """
        Override this method when using static table (ATTRIBUTE_TO_WATCH is not set).

        Raises:
            InvalidStaticDefinedError: When ATTRIBUTE_TO_WATCH has not been set without overriding the method.
        """
        if not self.should_be_dynamic:
            raise InvalidStaticDefinedError
        return []

    async def add_row(self, row_to_add: CliveCheckerboardTableRow) -> None:
        """
        Adds a row to the table. If no content widget is mounted, it will be removed and header will be mounted.

        Args:
            row_to_add: Row to add to the table.
        """
        has_rows_with_content = not bool(self.query(NoContentAvailable))

        with self.app.batch_update():
            if has_rows_with_content:
                await self.mount(row_to_add)
            else:
                await self.rows.remove()  # remove the special "no content" row
                await self.mount_all((self._header, row_to_add))

            self.update_cell_colors()

    async def remove_row(self, row_index: int) -> None:
        """
        Removes a row from the table. If no rows are left, no content widget will be mounted.

        Args:
            row_index: Index of the row to remove.
        """
        rows = self.rows

        assert 0 <= row_index < len(rows), "Row index out of range."

        is_last_row = len(rows) == 1
        row_to_remove = rows[row_index]

        with self.app.batch_update():
            await row_to_remove.remove()

            if is_last_row:
                await self._header.remove()
                await self.mount(self._get_no_content_available_widget())
            else:
                self.update_cell_colors()

    def filter(self, get_matchable: Callable[[CliveCheckerboardTableRow], Matchable], *filter_patterns: str) -> None:
        """
        Manage display of rows - hide rows that don't match the filter patterns.

        Args:
            get_matchable: Callback that extracts the Matchable object from a row for pattern comparison.
            *filter_patterns: Patterns used to filter rows.
        """
        if not filter_patterns:
            self.filter_clear()
            return

        for row in self.rows:
            row.display = get_matchable(row).is_matching_pattern(*filter_patterns)
        self.update_cell_colors()

    def filter_clear(self) -> None:
        for row in self.rows:
            row.display = True
        self.update_cell_colors()

    def _get_no_content_available_widget(self) -> Widget:
        return CliveCheckerboardTableRow(CliveCheckerBoardTableCell(NoContentAvailable(self.NO_CONTENT_TEXT)))

    def check_if_should_be_updated(self, content: ContentT) -> bool:  # noqa: ARG002
        """
        Must be overridden by the child class when using dynamic table.

        Args:
            content: The content to check if the table should be updated.

        Example:
            The previous value should be stored and compared against the new value.
            Implementation could look similar to:

            ```python
            def check_if_should_be_updated(self, content: ContentT) -> bool:
                return content.actual_value != self._previous_value
            ```


        Raises:
            InvalidDynamicDefinedError: When ATTRIBUTE_TO_WATCH has been set without overriding the method.

        Returns:
            Whether the table should be updated or not.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError
        return True

    def _set_evenness_styles(self, rows: Iterable[CliveCheckerboardTableRow], starting_index: int = 0) -> None:
        displayed_rows = [row for row in rows if row.display]

        for row_index, row in enumerate(displayed_rows):
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

    def is_anything_to_display(self, content: ContentT) -> bool:  # noqa: ARG002
        """Check whether there are elements to display. Should be overridden to create a custom condition."""
        return True

    def update_cell_colors(self) -> None:
        """Update background colors according to the actual displayed rows."""
        self._set_evenness_styles(self.rows)

    def update_previous_state(self, content: ContentT) -> None:  # noqa: ARG002
        """
        Must be overridden if the `ATTRIBUTE_TO_WATCH` class-var is set.

        Notice that you must also create your own previous state in the `__init__` method.
        """
        if self.should_be_dynamic:
            raise InvalidDynamicDefinedError
