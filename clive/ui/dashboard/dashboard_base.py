from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container
from textual.widgets import Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.storage.mock_database import NodeData, ProfileData


class Body(Container, can_focus=True):
    pass


class Section(Container):
    pass


class SectionTitle(Static):
    pass


class General(Section):
    def compose(self) -> ComposeResult:
        yield SectionTitle(self.__class__.__name__)
        yield TitledLabel(
            "My account",
            obj_to_watch=self.app,
            attribute_name="profile_data",
            callback=self.__get_account_name,
        )
        yield TitledLabel(
            "Reputation",
            obj_to_watch=self.app,
            attribute_name="node_data",
            callback=self.__get_reputation,
        )
        yield TitledLabel("Estimated account value", "10.24 USD")

    @staticmethod
    def __get_account_name(profile_data: ProfileData) -> str:
        return profile_data.active_account.name

    @staticmethod
    def __get_reputation(node_data: NodeData) -> str:
        return f"{node_data.reputation:.2f}"


class Accounts(Section):
    def compose(self) -> ComposeResult:
        yield SectionTitle(self.__class__.__name__)
        yield TitledLabel("Last owner update", "2021-01-01 00:00:00")
        yield TitledLabel("Last account update", "2021-01-01 00:00:00")
        yield TitledLabel("Recovery account", "hive.recovery")


class Money(Section):
    def compose(self) -> ComposeResult:
        yield SectionTitle(self.__class__.__name__)
        yield TitledLabel(
            "HIVE balance",
            obj_to_watch=self.app,
            attribute_name="node_data",
            callback=self.__get_hive_balance,
        )
        yield TitledLabel(
            "HP balance",
            obj_to_watch=self.app,
            attribute_name="node_data",
            callback=self.__get_hp_balance,
        )
        yield TitledLabel(
            "HBD balance",
            obj_to_watch=self.app,
            attribute_name="node_data",
            callback=self.__get_hbd_balance,
        )
        yield TitledLabel(
            "HIVE savings balance",
            obj_to_watch=self.app,
            attribute_name="node_data",
            callback=self.__get_hive_savings_balance,
        )
        yield TitledLabel(
            "HBD savings balance",
            obj_to_watch=self.app,
            attribute_name="node_data",
            callback=self.__get_hbd_savings_balance,
        )

    @staticmethod
    def __get_hive_balance(node_data: NodeData) -> str:
        return f"{node_data.hive_balance:.2f} HIVE"

    @staticmethod
    def __get_hp_balance(node_data: NodeData) -> str:
        return f"{node_data.hive_power_balance:.2f} HP"

    @staticmethod
    def __get_hbd_balance(node_data: NodeData) -> str:
        return f"{node_data.hive_dollars:.2f} HBD"

    @staticmethod
    def __get_hive_savings_balance(node_data: NodeData) -> str:
        return f"{node_data.hive_savings:.2f} HIVE"

    @staticmethod
    def __get_hbd_savings_balance(node_data: NodeData) -> str:
        return f"{node_data.hbd_savings:.2f} HBD"


class Powers(Section):
    def compose(self) -> ComposeResult:
        yield SectionTitle(self.__class__.__name__)
        yield TitledLabel(
            "Resource credits (RC)",
            obj_to_watch=self.app,
            attribute_name="node_data",
            callback=self.__get_rc,
        )
        yield TitledLabel(
            "Voting power",
            obj_to_watch=self.app,
            attribute_name="node_data",
            callback=self.__get_voting_power,
        )
        yield TitledLabel(
            "Down voting power",
            obj_to_watch=self.app,
            attribute_name="node_data",
            callback=self.__get_down_voting_power,
        )

    @staticmethod
    def __get_rc(node_data: NodeData) -> str:
        return f"{node_data.rc:.2f} %"

    @staticmethod
    def __get_voting_power(node_data: NodeData) -> str:
        return f"{node_data.voting_power:.2f} %"

    @staticmethod
    def __get_down_voting_power(node_data: NodeData) -> str:
        return f"{node_data.down_vote_power:.2f} %"


class History(Section):
    def compose(self) -> ComposeResult:
        yield SectionTitle(self.__class__.__name__)
        yield Static("No history")


class DashboardBase(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        yield Body(
            General(),
            Accounts(),
            Money(),
            Powers(),
            History(),
        )

    def on_mount(self) -> None:
        self.query_one(Body).focus()
