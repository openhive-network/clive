from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import HSplit, VSplit, Window
from prompt_toolkit.widgets import Box, Checkbox, Label, TextArea

from clive.ui.component import Component
from clive.ui.widgets.horizontal_space import HorizontalSpace

if TYPE_CHECKING:
    from clive.models.operation import Operation
    from clive.ui.operation_summary.operation_summary_view import OperationSummaryView


class OperationSummaryPanel(Component["OperationSummaryView"]):
    def __init__(self, parent: OperationSummaryView, operation: Operation):
        self.__operation = operation
        super().__init__(parent)

    def _create_container(self) -> HSplit:
        return HSplit(
            [
                self.__title(),
                Box(
                    HSplit(
                        [
                            VSplit(
                                [
                                    self.__operation_info(),
                                    self.__balance_info(),
                                ]
                            ),
                            HorizontalSpace(),
                            self.__signing_info(),
                            self.__broadcast(),
                        ]
                    ),
                    padding=0,
                    padding_top=1,
                ),
                Window(),
            ],
            style="class:secondary",
        )

    def __title(self) -> Label:
        return Label("Operation summary", style="#000000 bold")

    def __operation_info(self) -> Box:
        return Box(
            HSplit(
                [
                    Label(f"Operation: {self.__operation.type_}"),
                    Box(
                        TextArea(text=self.__operation.as_yaml(), focusable=False, style="class:primary"),
                        padding=0,
                        padding_left=1,
                    ),
                ]
            ),
            padding=0,
            padding_right=2,
        )

    def __balance_info(self) -> HSplit:
        return HSplit(
            [
                Label("HIVE balance before: 5330 HIVE"),
                Label("HIVE balance after: 5300 HIVE"),
            ]
        )

    def __signing_info(self) -> Label:
        return Label("sign using imported key: My active key")

    def __broadcast(self) -> Checkbox:
        return Checkbox("Broadcast operation", checked=True)
