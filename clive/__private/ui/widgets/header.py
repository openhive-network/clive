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
    from collections.abc import Callable

    from textual import events
    from textual.app import ComposeResult

    from clive.__private.core.app_state import AppState
    from clive.__private.storage.mock_database import Account


class HeaderIcon(TextualHeaderIcon):
    def __init__(self) -> None:
        super().__init__(id="icon")

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.on_header_expanded)

    def on_header_expanded(self, expanded: bool) -> None:
        self.icon = "-" if expanded else "+"


class AlarmDisplay(DynamicLabel):
    def __init__(
        self,
        account_getter: Callable[[ProfileData], list[Account]],
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

        self.__label = AlarmDisplay(lambda pd: [pd.working_account, *pd.watched_accounts])

    def compose(self) -> ComposeResult:
        yield self.__label


class DynamicPropertiesClock(Horizontal, CliveWidget):
    last_update_trigger = var(False)
    """A value that is used to trigger a re-rendering of the last update time."""

    def compose(self) -> ComposeResult:
        self.set_interval(0.5, self.__trigger_last_update)

        yield DynamicLabel(self.app.world, "app_state", self.__get_block_num, id_="block_num")
        yield DynamicLabel(self.app.world, "app_state", self.__get_chain_time, id_="chain_time")
        yield DynamicLabel(self, "last_update_trigger", self.__get_last_update, id_="last_update")

    def __get_block_num(self, app_state: AppState) -> str:
        return f"block: {app_state.get_dynamic_global_properties().head_block_number}"

    def __get_chain_time(self, app_state: AppState) -> str:
        return f"{app_state.get_dynamic_global_properties().time.time()} UTC"

    def __get_last_update(self, _: bool) -> str:
        gdpo = self.app.world.app_state.get_dynamic_global_properties()
        last_update = humanize.naturaltime(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - gdpo.time)
        return f"last update: {last_update}"

    def __trigger_last_update(self) -> None:
        self.last_update_trigger = not self.last_update_trigger


class Header(TextualHeader, CliveWidget):
    def __init__(self) -> None:
        super().__init__()
        self.on_app_state(self.app.world.app_state)

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.on_header_expanded)
        self.watch(self.app.world, "app_state", self.on_app_state, init=False)

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        with Horizontal(id="bar"):
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
                    callback=lambda app_state: "active" if app_state.is_active() else "inactive",
                    id_="mode-label",
                )
            yield DynamicPropertiesClock()

        with Vertical(id="expandable"):
            yield HeaderTitle()
            yield TitledLabel(
                "node address",
                obj_to_watch=self.app.world,
                attribute_name="profile_data",
                callback=self.__get_node_address,
                id_="node-address-label",
            )

    def on_click(self, event: events.Click) -> None:  # type: ignore
        event.prevent_default()
        self.app.header_expanded = not self.app.header_expanded

    def on_header_expanded(self, expanded: bool) -> None:
        self.add_class("-tall") if expanded else self.remove_class("-tall")

    def on_app_state(self, app_state: AppState) -> None:
        if app_state.is_active():
            self.add_class("-active")
        else:
            self.remove_class("-active")

    @staticmethod
    def __get_node_address(profile_data: ProfileData) -> str:
        return str(profile_data.node_address)

    @staticmethod
    def __get_profile_name(profile_data: ProfileData) -> str:
        return profile_data.name

    def __is_in_onboarding_mode(self) -> bool:
        return self.app.world.profile_data.name == ProfileData.ONBOARDING_PROFILE_NAME
