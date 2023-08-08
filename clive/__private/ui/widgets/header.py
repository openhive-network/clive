from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import humanize
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import var
from textual.widgets import Header as TextualHeader
from textual.widgets._header import HeaderIcon as TextualHeaderIcon
from textual.widgets._header import HeaderTitle

from clive.__private.core.profile_data import ProfileData
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from textual import events
    from textual.app import ComposeResult

    from clive.__private.core.app_state import AppState
    from clive.__private.core.node.node import Node
    from clive.__private.storage.accounts import Account


class HeaderIcon(TextualHeaderIcon):
    def __init__(self) -> None:
        super().__init__(id="icon")

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.header_expanded_changed)

    def header_expanded_changed(self, expanded: bool) -> None:
        self.icon = "-" if expanded else "+"


class AlarmDisplay(DynamicLabel):
    def __init__(
        self,
        account_getter: Callable[[ProfileData], Iterable[Account]],
        init: str | None = None,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        def update_callback(pd: ProfileData) -> str:
            class_name = "-no-alarm"
            alarm_count = sum([acc.data.warnings for acc in account_getter(pd)])
            if alarm_count:
                self.remove_class(class_name)
                return f"!{alarm_count}x ALARMS!"
            self.add_class(class_name)
            return "No alarms"

        super().__init__(self.app.world, "profile_data", update_callback, init=init, id_=id_, classes=classes)


class AlarmsSummary(Container, CliveWidget):
    def __init__(self) -> None:
        super().__init__()

        self.__label = AlarmDisplay(lambda pd: pd.get_tracked_accounts())

    def compose(self) -> ComposeResult:
        yield self.__label


class DynamicPropertiesClock(Horizontal, CliveWidget):
    last_update_trigger = var(False)
    """A value that is used to trigger a re-rendering of the last update time."""

    def compose(self) -> ComposeResult:
        self.set_interval(0.25, self.__trigger_last_update)

        yield TitledLabel(
            "Block",
            obj_to_watch=self.app.world,
            attribute_name="app_state",
            callback=self.__get_last_block,
            id_="block_num",
        )
        yield TitledLabel(
            "Last update",
            obj_to_watch=self,
            attribute_name="last_update_trigger",
            callback=self.__get_last_update,
            id_="last_update",
        )

    def __get_last_block(self, app_state: AppState) -> str:
        block_num = app_state.get_dynamic_global_properties().head_block_number
        block_time = app_state.get_dynamic_global_properties().time.time()
        return f"{block_num} ({block_time} UTC)"

    def __get_last_update(self, _: bool) -> str:
        gdpo = self.app.world.app_state.get_dynamic_global_properties()
        return humanize.naturaltime(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - gdpo.time)

    def __trigger_last_update(self) -> None:
        self.last_update_trigger = not self.last_update_trigger


class Header(TextualHeader, CliveWidget):
    def __init__(self) -> None:
        super().__init__()
        self.app_state_changed(self.app.world.app_state)
        self.__node_version_label = DynamicLabel(
            obj_to_watch=self.app.world,
            attribute_name="node",
            callback=self.__get_node_version,
            id_="node-type-label",
        )

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.header_expanded_changed)
        self.watch(self.app.world, "app_state", self.app_state_changed, init=False)

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        with Horizontal(id="bar"):
            yield self.__node_version_label
            if not self.__is_in_onboarding_mode():
                yield TitledLabel(
                    "Profile",
                    obj_to_watch=self.app.world,
                    attribute_name="profile_data",
                    callback=self.__get_profile_name,
                    id_="profile-label",
                )
                yield AlarmsSummary()

                yield TitledLabel(
                    "Mode",
                    obj_to_watch=self.app.world,
                    attribute_name="app_state",
                    callback=lambda app_state: "active" if app_state.is_active else "inactive",
                    id_="mode-label",
                )
            yield DynamicPropertiesClock()

        with Vertical(id="expandable"):
            yield HeaderTitle()
            yield TitledLabel(
                "node address",
                obj_to_watch=self.app.world,
                attribute_name="node",
                callback=self.__get_node_address,
                id_="node-address-label",
            )

    def on_click(self, event: events.Click) -> None:
        event.prevent_default()
        self.app.header_expanded = not self.app.header_expanded

    def header_expanded_changed(self, expanded: bool) -> None:
        self.add_class("-tall") if expanded else self.remove_class("-tall")

    def app_state_changed(self, app_state: AppState) -> None:
        if app_state.is_active:
            self.add_class("-active")
        else:
            self.remove_class("-active")

    @staticmethod
    def __get_node_address(node: Node) -> str:
        return str(node.address)

    @staticmethod
    def __get_profile_name(profile_data: ProfileData) -> str:
        return profile_data.name

    def __get_node_version(self, node: Node) -> str:
        class_to_switch = "-not-mainnet"
        if node.network_type == "mainnet":
            self.__node_version_label.remove_class(class_to_switch)
        else:
            self.__node_version_label.add_class(class_to_switch)
        return node.network_type

    def __is_in_onboarding_mode(self) -> bool:
        return self.app.world.profile_data.name == ProfileData.ONBOARDING_PROFILE_NAME
