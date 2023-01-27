from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from prompt_toolkit import HTML
from prompt_toolkit.layout import HSplit, VSplit, Window
from prompt_toolkit.widgets import Frame, HorizontalLine, Label, ProgressBar, VerticalLine

from clive.storage.mock_database import MockDB
from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.dashboard.dashboard import Dashboard  # noqa: F401


class AccountInfo(Component["Dashboard"]):
    def __init__(self, parent: Dashboard) -> None:
        self.__progress_bar = ProgressBar()
        super().__init__(parent)

    def _create_container(self) -> HSplit:
        return HSplit(
            [
                self.__warnings(),
                Window(),
                VSplit(
                    [
                        HSplit(
                            [
                                self.__general(),
                                self.__money(),
                            ]
                        ),
                        VerticalLine(),
                        HSplit(
                            [
                                self.__accounts(),
                                self.__powers(),
                                HorizontalLine(),
                                self.__recurrent_transfer(),
                            ]
                        ),
                    ],
                ),
            ],
            style="class:secondary",
        )

    def __warnings(self) -> HSplit:
        return HSplit(
            [
                Label("WARNINGS", style="bold"),
                *self.__get_warning_messages(),
            ],
            style="class:red",
        )

    def __get_warning_messages(self) -> Generator[Label, None, None]:
        warnings = [
            "Your account will expire in 10 days if you don't vote for witness or proposal.",
            "The watched account: @gtg changed the owner authority.",
        ]
        for idx, warning in enumerate(warnings):
            yield Label(f"{idx + 1}. {warning}")

    def __general(self) -> Frame:
        return Frame(
            HSplit(
                [
                    VSplit(
                        [
                            HSplit([Label("Account name:"), Label("Reputation:")]),
                            HSplit(
                                [
                                    Label("@cookingwithKasia"),
                                    Label("67"),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            title=HTML("<black><b>GENERAL</b></black>"),
        )

    def __money(self) -> HSplit:
        return HSplit(
            [
                Label("\nMONEY"),
                VSplit(
                    [
                        HSplit(
                            [
                                Label("HIVE balance:"),
                                Label("HIVE POWER balance:"),
                                Label("HIVE DOLLARS:"),
                                Label("SAVINGS balance HIVE:"),
                                Label("SAVINGS balance HBD:"),
                                Label("Unclaimed rewards:"),
                                Label("Unclaimed rewards:"),
                                Label("Unclaimed rewards:"),
                            ]
                        ),
                        HSplit(
                            [
                                Label(lambda: f"{MockDB.node.hive_balance :.2f} HIVE"),
                                Label(lambda: f"{MockDB.node.hive_power_balance :.2f} HP"),
                                Label(lambda: f"${MockDB.node.hive_dollars :.2f}"),
                                Label(lambda: f"{MockDB.node.hive_savings :.2f} HIVE"),
                                Label(lambda: f"{MockDB.node.hbd_savings :.2f} HBD"),
                                Label(lambda: f"{MockDB.node.hbd_unclaimed :.2f} HBD"),
                                Label(lambda: f"{MockDB.node.hp_unclaimed :.2f} HP"),
                                Label(lambda: f"{MockDB.node.hive_unclaimed :.2f} HIVE"),
                            ]
                        ),
                    ]
                ),
            ]
        )

    def __accounts(self) -> Frame:
        return Frame(
            HSplit(
                [
                    VSplit(
                        [
                            HSplit(
                                [Label("Last owner update:"), Label("Last account update:"), Label("Recovery account:")]
                            ),
                            HSplit(
                                [
                                    Label("01.06.2022 19:48"),
                                    Label("14.12.2022 22:21"),
                                    Label("@hive.recovery"),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            title=HTML("<black><b>ACCOUNTS</b></black>"),
        )

    def __update_progress_bar(self) -> str:
        self.__progress_bar.percentage = MockDB.node.rc
        return "Resource Credits (RC):"

    def __powers(self) -> Frame:
        return Frame(
            title=HTML("<black><b>POWERS</b></black>"),
            body=VSplit(
                [
                    HSplit(
                        [
                            Label(self.__update_progress_bar),
                            Label("100% charged in:"),
                            Label("Voting Power:"),
                            Label("100% charged in:"),
                            Label("Down vote Power:"),
                            Label("100% charged in:"),
                        ]
                    ),
                    HSplit(
                        [
                            self.__progress_bar,
                            Label("2 days"),
                            Label(lambda: f"{MockDB.node.voting_power :.2f}%"),
                            Label("2 days"),
                            Label(lambda: f"{MockDB.node.down_vote_power :.2f}%"),
                            Label("4 days"),
                        ]
                    ),
                ]
            ),
        )

    def __recurrent_transfer(self) -> HSplit:
        return HSplit(
            [
                Label("\nRECURRENT TRANSFER"),
                VSplit(
                    [
                        HSplit(
                            [
                                Label("Pending transfers:"),
                                Label("Next recurrent transfer date:"),
                                Label("Next recurrent transfer amount:"),
                            ]
                        ),
                        HSplit(
                            [
                                Label("2"),
                                Label("01.06.2023"),
                                Label("300 HIVE"),
                            ]
                        ),
                    ]
                ),
            ]
        )
