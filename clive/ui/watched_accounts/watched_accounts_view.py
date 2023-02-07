from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import HSplit, VSplit, WindowAlign
from prompt_toolkit.widgets import Box, Button, Frame, HorizontalLine, Label, VerticalLine

from clive.ui.containerable import Containerable
from clive.ui.view import View
from clive.ui.widgets.progress_bar import ProgressBar

cell_width = 15  # Dimension(weight=3)


class _Row(Containerable[Frame]):
    def __init__(self, name: str, reputation: int, hive_balance: int, hive_savings: int, rc: int,
                 warnings: int) -> None:
        self.name = name
        self.reputation = reputation
        self.hive_balance = hive_balance
        self.hive_savings = hive_savings
        self.rc = rc
        self.warnings = warnings
        super().__init__()

    def _create_container(self):
        kb = KeyBindings()

        kb.add("up")(focus_previous)
        kb.add("down")(focus_next)

        return Box(Frame(
            VSplit([
                Button(text="SELECT", width=cell_width),
                VerticalLine(),
                CenteredLabel(text=self.name, width=cell_width),
                VerticalLine(),
                CenteredLabel(text=f"{self.reputation}", width=cell_width),
                VerticalLine(),
                CenteredLabel(text=f"{self.hive_balance}", width=cell_width),
                VerticalLine(),
                CenteredLabel(text=f"{self.hive_savings}", width=cell_width),
                VerticalLine(),
                VSplit([ProgressBar()], width=cell_width),
                VerticalLine(),
                CenteredLabel(text=f"{self.warnings}", width=cell_width),
            ]),
            key_bindings=kb,
        ),
            padding=0

        )


class WatchedAccountsView(View):
    def _create_container(self) -> HSplit:
        return HSplit([
            self.__header(),
            HorizontalLine(),
            self.__body(),
        ])

    def __header(self) -> VSplit:
        return VSplit([
            CenteredLabel(text="", width=cell_width),
            VerticalLine(),
            CenteredLabel(text="Name", width=cell_width),
            VerticalLine(),
            CenteredLabel(text="Reputation", width=cell_width),
            VerticalLine(),
            CenteredLabel(text="HIVE Balance", width=cell_width),
            VerticalLine(),
            CenteredLabel(text="HIVE Savings", width=cell_width),
            VerticalLine(),
            CenteredLabel(text="RC", width=cell_width),
            VerticalLine(),
            CenteredLabel(text="Warnings", width=cell_width),
        ])

    def __body(self) -> HSplit:
        return HSplit([
            _Row(
                name="account01",
                reputation=67,
                hive_balance=1512,
                hive_savings=100,
                rc=5,
                warnings=5,
            ).container,
            _Row(
                name="account015453",
                reputation=63427,
                hive_balance=151442,
                hive_savings=1300,
                rc=53,
                warnings=5,
            ).container,
            _Row(
                name="account01",
                reputation=67,
                hive_balance=1512,
                hive_savings=100,
                rc=5,
                warnings=5,
            ).container,
            _Row(
                name="account016546546546545465464645",
                reputation=67,
                hive_balance=1512,
                hive_savings=100,
                rc=5,
                warnings=5,
            ).container,
        ]
        )


class CenteredLabel(Label):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, align=WindowAlign.CENTER)
