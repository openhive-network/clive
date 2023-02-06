from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit import HTML
from prompt_toolkit.layout import HSplit, VSplit, Window
from prompt_toolkit.widgets import Frame, HorizontalLine, Label, VerticalLine

from clive.storage.mock_database import MockDB
from clive.ui.component import Component
from clive.ui.widgets.progress_bar import ProgressBar

if TYPE_CHECKING:
    from clive.ui.dashboard.dashboard import Dashboard  # noqa: F401


class AccountInfo(Component["Dashboard"]):
    def __init__(self, parent: Dashboard) -> None:
        self.__rc_progress_bar = ProgressBar()
        self.__voting_power_progress_bar = ProgressBar()
        self.__down_vote_power_progress_bar = ProgressBar()
        super().__init__(parent)

    def _create_container(self) -> HSplit:
        return HSplit(
            [
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
                            ],
                        ),
                    ],
                ),
                Window(),
            ],
            style="class:secondary",
        )

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

    def __update_rc_progress_bar(self) -> str:
        self.__rc_progress_bar.percentage = MockDB.node.rc
        return "Resource Credits (RC):"

    def __update_voting_power_progress_bar(self) -> str:
        self.__voting_power_progress_bar.percentage = MockDB.node.voting_power
        return "Voting Power:"

    def __update_down_vote_power_progress_bar(self) -> str:
        self.__down_vote_power_progress_bar.percentage = MockDB.node.down_vote_power
        return "Down Vote Power:"

    def __powers(self) -> Frame:
        return Frame(
            title=HTML("<black><b>POWERS</b></black>"),
            body=VSplit(
                [
                    HSplit(
                        [
                            Label(self.__update_rc_progress_bar),
                            Label("100% charged in:"),
                            Label(self.__update_voting_power_progress_bar),
                            Label("100% charged in:"),
                            Label(self.__update_down_vote_power_progress_bar),
                            Label("100% charged in:"),
                        ]
                    ),
                    HSplit(
                        [
                            self.__rc_progress_bar,
                            Label("2 days"),
                            self.__voting_power_progress_bar,
                            Label("2 days"),
                            self.__down_vote_power_progress_bar,
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
