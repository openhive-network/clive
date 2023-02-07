from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Union

from prompt_toolkit.layout import UIControl
from prompt_toolkit.layout.containers import AnyContainer, HorizontalAlign, HSplit, VerticalAlign, VSplit, Window
from prompt_toolkit.layout.dimension import (
    AnyDimension,
    Dimension,
    max_layout_dimensions,
    sum_layout_dimensions,
    to_dimension,
)
from prompt_toolkit.utils import take_using_weights

from clive.ui.widgets.table.table_border import TableBorder

if TYPE_CHECKING:
    from clive.ui.widgets.table.table_border import TableBorderT


class Merge:
    def __init__(self, cell: AnyContainer, merge: int = 1):
        self.__cell = cell
        self.__merge = merge

    @property
    def cm(self) -> tuple[AnyContainer, int]:
        return self.__cell, self.__merge


AnyElement = Union[AnyContainer, Merge, UIControl]

AnyTable = Union[
    AnyElement,
    Sequence[AnyElement],
    Sequence[Sequence[AnyElement]],
]


class TableContainer(HSplit):
    def __init__(
        self,
        table: AnyTable,
        border: TableBorderT = TableBorder.THIN,
        column_width: AnyDimension = None,
        column_widths: Sequence[AnyDimension] = (),
        window_too_small=None,
        align=VerticalAlign.JUSTIFY,
        padding=0,
        padding_char=None,
        padding_style="",
        width=None,
        height=None,
        z_index=None,
        modal=False,
        key_bindings=None,
        style="",
    ):
        self.border = border
        self.column_width = column_width
        self.column_widths = column_widths

        # ensure the table is iterable (has rows)
        if not isinstance(table, list):
            table = [table]
        children = [_Row(row=row, table=self, border=border) for row in table]

        super().__init__(
            children=children,
            window_too_small=window_too_small,
            align=align,
            padding=padding,
            padding_char=padding_char,
            padding_style=padding_style,
            width=width,
            height=height,
            z_index=z_index,
            modal=modal,
            key_bindings=key_bindings,
            style=style,
        )

    @property
    def columns(self):
        return max(row.raw_columns for row in self.children)

    @property
    def _all_children(self):
        """
        List of child objects, including padding & border.
        """

        def get():
            result = []

            # Padding top.
            if self.align in (VerticalAlign.CENTER, VerticalAlign.BOTTOM):
                result.append(Window(width=Dimension(preferred=0)))

            # Border top is first inserted in children loop.

            # The children with padding.
            prev = None
            for child in self.children:
                result.append(_Border(prev=prev, next=child, table=self, border=self.border))
                result.append(child)
                prev = child

            # Border bottom.
            result.append(_Border(prev=prev, next=None, table=self, border=self.border))

            # Padding bottom.
            if self.align in (VerticalAlign.CENTER, VerticalAlign.TOP):
                result.append(Window(width=Dimension(preferred=0)))

            return result

        return self._children_cache.get(tuple(self.children), get)

    def preferred_dimensions(self, width):
        dimensions = [[]] * self.columns
        for row in self.children:
            assert isinstance(row, _Row)
            j = 0
            for cell in row.children:
                assert isinstance(cell, _Cell)

                if cell.merge != 1:
                    dimensions[j].append(cell.preferred_width(width))

                j += cell.merge

        for i, c in enumerate(dimensions):
            yield Dimension.exact(1)

            try:
                w = self.column_widths[i]
            except IndexError:
                w = self.column_width
            if w is None:  # fitted
                yield max_layout_dimensions(c)
            else:  # fixed or weighted
                yield to_dimension(w)
        yield Dimension.exact(1)


class _VerticalBorder(Window):
    def __init__(self, border):
        super().__init__(width=1, char=border.VERTICAL)


class _HorizontalBorder(Window):
    def __init__(self, border: TableBorderT):
        super().__init__(height=1, char=border.HORIZONTAL)


class _UnitBorder(Window):
    def __init__(self, char):
        super().__init__(width=1, height=1, char=char)


class _BaseRow(VSplit):
    @property
    def columns(self):
        return self.table.columns

    def _divide_widths(self, width):
        """
        Return the widths for all columns.
        Or None when there is not enough space.
        """
        children = self._all_children

        if not children:
            return []

        # Calculate widths.
        dimensions = list(self.table.preferred_dimensions(width))
        preferred_dimensions = [d.preferred for d in dimensions]

        # Sum dimensions
        sum_dimensions = sum_layout_dimensions(dimensions)

        # If there is not enough space for both.
        # Don't do anything.
        if sum_dimensions.min > width:
            return

        # Find optimal sizes. (Start with minimal size, increase until we cover
        # the whole width.)
        sizes = [d.min for d in dimensions]

        child_generator = take_using_weights(items=list(range(len(dimensions))), weights=[d.weight for d in dimensions])

        i = next(child_generator)

        # Increase until we meet at least the 'preferred' size.
        preferred_stop = min(width, sum_dimensions.preferred)

        while sum(sizes) < preferred_stop:
            if sizes[i] < preferred_dimensions[i]:
                sizes[i] += 1
            i = next(child_generator)

        # Increase until we use all the available space.
        max_dimensions = [d.max for d in dimensions]
        max_stop = min(width, sum_dimensions.max)

        while sum(sizes) < max_stop:
            if sizes[i] < max_dimensions[i]:
                sizes[i] += 1
            i = next(child_generator)

        # perform merges if necessary
        if len(children) != len(sizes):
            tmp = []
            i = 0
            for c in children:
                if isinstance(c, _Cell):
                    inc = (c.merge * 2) - 1
                    tmp.append(sum(sizes[i : i + inc]))
                else:
                    inc = 1
                    tmp.append(sizes[i])
                i += inc
            sizes = tmp

        return sizes


class _Row(_BaseRow):
    def __init__(
        self,
        row,
        table,
        border,
        window_too_small=None,
        align=HorizontalAlign.JUSTIFY,
        padding=Dimension.exact(0),
        padding_char=None,
        padding_style="",
        width=None,
        height=None,
        z_index=None,
        modal=False,
        key_bindings=None,
        style="",
    ):
        self.table = table
        self.border = border

        # ensure the row is iterable (has cells)
        if not isinstance(row, list):
            row = [row]
        children = []
        for c in row:
            m = 1
            if isinstance(c, Merge):
                c, m = c.cm
            elif isinstance(c, dict):
                c, m = Merge(**c).cm
            children.append(_Cell(cell=c, table=table, row=self, merge=m))

        super().__init__(
            children=children,
            window_too_small=window_too_small,
            align=align,
            padding=padding,
            padding_char=padding_char,
            padding_style=padding_style,
            width=width,
            height=height,
            z_index=z_index,
            modal=modal,
            key_bindings=key_bindings,
            style=style,
        )

    @property
    def raw_columns(self):
        return sum(cell.merge for cell in self.children)

    @property
    def _all_children(self):
        """
        List of child objects, including padding & border.
        """

        def get():
            result = []

            # Padding left.
            if self.align in (HorizontalAlign.CENTER, HorizontalAlign.RIGHT):
                result.append(Window(width=Dimension(preferred=0)))

            # Border left is first inserted in children loop.

            # The children with padding.
            c = 0
            for child in self.children:
                result.append(_VerticalBorder(border=self.border))
                result.append(child)
                c += child.merge
            # Fill in any missing columns
            for _ in range(self.columns - c):
                result.append(_VerticalBorder(border=self.border))
                result.append(_Cell(cell=None, table=self.table, row=self))

            # Border right.
            result.append(_VerticalBorder(border=self.border))

            # Padding right.
            if self.align in (HorizontalAlign.CENTER, HorizontalAlign.LEFT):
                result.append(Window(width=Dimension(preferred=0)))

            return result

        return self._children_cache.get(tuple(self.children), get)


class _Border(_BaseRow):
    def __init__(
        self,
        prev,
        next,
        table,
        border: TableBorderT,
        window_too_small=None,
        align=HorizontalAlign.JUSTIFY,
        padding=Dimension.exact(0),
        padding_char=None,
        padding_style="",
        width=None,
        height=None,
        z_index=None,
        modal=False,
        key_bindings=None,
        style="",
    ):
        assert prev or next
        self.prev = prev
        self.next = next
        self.table = table
        self.border = border

        children = [_HorizontalBorder(border=border)] * self.columns

        super().__init__(
            children=children,
            window_too_small=window_too_small,
            align=align,
            padding=padding,
            padding_char=padding_char,
            padding_style=padding_style,
            width=width,
            height=height or 1,
            z_index=z_index,
            modal=modal,
            key_bindings=key_bindings,
            style=style,
        )

    def has_border(self, row):
        yield None  # first (outer) border

        if not row:
            # this row is undefined, none of the border need to be marked
            yield from [False] * (self.columns - 1)
        else:
            c = 0
            for child in row.children:
                yield from [False] * (child.merge - 1)
                yield True
                c += child.merge

            yield from [True] * (self.columns - c)

        yield None  # last (outer) border

    @property
    def _all_children(self):
        """
        List of child objects, including padding & border.
        """

        def get():
            result = []

            # Padding left.
            if self.align in (HorizontalAlign.CENTER, HorizontalAlign.RIGHT):
                result.append(Window(width=Dimension(preferred=0)))

            def char(i, pc=False, nc=False):
                if i == 0:
                    if self.prev and self.next:
                        return self.border.LEFT_T
                    elif self.prev:
                        return self.border.BOTTOM_LEFT
                    else:
                        return self.border.TOP_LEFT

                if i == self.columns:
                    if self.prev and self.next:
                        return self.border.RIGHT_T
                    elif self.prev:
                        return self.border.BOTTOM_RIGHT
                    else:
                        return self.border.TOP_RIGHT

                if pc and nc:
                    return self.border.INTERSECT
                elif pc:
                    return self.border.BOTTOM_T
                elif nc:
                    return self.border.TOP_T
                else:
                    return self.border.HORIZONTAL

            # Border left is first inserted in children loop.

            # The children with padding.
            pcs = self.has_border(self.prev)
            ncs = self.has_border(self.next)
            for i, (child, pc, nc) in enumerate(zip(self.children, pcs, ncs)):
                result.append(_UnitBorder(char=char(i, pc, nc)))
                result.append(child)

            # Border right.
            result.append(_UnitBorder(char=char(self.columns)))

            # Padding right.
            if self.align in (HorizontalAlign.CENTER, HorizontalAlign.LEFT):
                result.append(Window(width=Dimension(preferred=0)))

            return result

        return self._children_cache.get(tuple(self.children), get)


class _Cell(HSplit):
    def __init__(
        self,
        cell,
        table,
        row,
        merge: int = 1,
        padding: int = 0,
        char=None,
        padding_left=None,
        padding_right=None,
        padding_top=None,
        padding_bottom=None,
        window_too_small=None,
        width=None,
        height=None,
        z_index=None,
        modal=False,
        key_bindings=None,
        style="",
    ):
        self.table = table
        self.row = row
        self.merge = merge

        if padding is None:
            padding = Dimension(preferred=0)

        def get(value):
            if value is None:
                value = padding
            return to_dimension(value)

        self.padding_left = get(padding_left)
        self.padding_right = get(padding_right)
        self.padding_top = get(padding_top)
        self.padding_bottom = get(padding_bottom)

        children = []
        children.append(Window(width=self.padding_left, char=char))
        if cell:
            children.append(cell)
        children.append(Window(width=self.padding_right, char=char))

        children = [
            Window(height=self.padding_top, char=char),
            VSplit(children),
            Window(height=self.padding_bottom, char=char),
        ]

        super().__init__(
            children=children,
            window_too_small=window_too_small,
            width=width,
            height=height,
            z_index=z_index,
            modal=modal,
            key_bindings=key_bindings,
            style=style,
        )
