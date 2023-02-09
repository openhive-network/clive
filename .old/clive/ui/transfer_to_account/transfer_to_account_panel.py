from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import AnyContainer, HSplit, VSplit, Window
from prompt_toolkit.widgets import Box, Label, TextArea

from clive.app_status import app_status
from clive.ui.component import Component
from clive.ui.widgets.horizontal_space import HorizontalSpace
from clive.ui.widgets.progress_bar import ProgressBar

if TYPE_CHECKING:
    from clive.ui.transfer_to_account.transfer_to_account_view import TransferToAccountView


class TransferToAccountPanel(Component["TransferToAccountView"]):
    def __init__(self, parent: TransferToAccountView):
        self.__asset = parent.asset

        self.__to_input = TextArea(focus_on_click=True, style="class:tertiary underline")
        self.__amount_input = TextArea(focus_on_click=True, style="class:tertiary underline")
        self.__memo_input = TextArea(focus_on_click=True, style="class:tertiary underline")

        super().__init__(parent)

    @property
    def to(self) -> str:
        return self.__to_input.text

    @property
    def amount(self) -> str:
        return self.__amount_input.text

    @property
    def memo(self) -> str:
        return self.__memo_input.text

    def _create_container(self) -> AnyContainer:
        return HSplit(
            [
                self.__title(),
                Box(
                    VSplit(
                        [
                            self.__transfer_info(),
                            self.__credits_info(),
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
        return Label(f"{self.__asset} transfer to account - prepare operation", style="#000000 bold")

    def __transfer_info(self) -> Box:
        return Box(
            VSplit(
                [
                    HSplit(
                        [
                            Label("from:"),
                            HorizontalSpace(),
                            Label("to:"),
                            HorizontalSpace(),
                            Label(f"amount ({self.__asset}):"),
                            HorizontalSpace(),
                            Label("memo:"),
                        ]
                    ),
                    HSplit(
                        [
                            Label(app_status.current_profile),
                            HorizontalSpace(),
                            self.__to_input,
                            HorizontalSpace(),
                            self.__amount_input,
                            HorizontalSpace(),
                            self.__memo_input,
                        ]
                    ),
                ]
            ),
            padding=0,
            padding_right=2,
        )

    def __credits_info(self) -> VSplit:
        return VSplit(
            [
                HSplit(
                    [
                        Label(f"{self.__asset} balance:"),
                        Label("Resource credits (RC:"),
                        Label("Enough credits for approximately:"),
                    ]
                ),
                HSplit(
                    [
                        Label("5330 HIVE"),
                        ProgressBar(),
                        Label("17 transfers"),
                    ]
                ),
            ]
        )
