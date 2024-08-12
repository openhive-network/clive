from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Center, Horizontal, Vertical
from textual.reactive import var
from textual.widgets import Header as TextualHeader
from textual.widgets._header import HeaderIcon as TextualHeaderIcon
from textual.widgets._header import HeaderTitle

from clive.__private.core.date_utils import utc_now
from clive.__private.core.formatters.data_labels import NOT_AVAILABLE_LABEL
from clive.__private.core.formatters.humanize import humanize_natural_time
from clive.__private.core.profile_data import ProfileData
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.alarm_display import AlarmDisplay
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.titled_label import TitledLabel
from clive.exceptions import CommunicationError

if TYPE_CHECKING:
    from textual import events
    from textual.app import ComposeResult
    from textual.events import Mount

    from clive.__private.core.app_state import AppState
    from clive.__private.core.node.node import Node


class HeaderIcon(TextualHeaderIcon):
    def __init__(self) -> None:
        super().__init__(id="icon")

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.header_expanded_changed)

    def header_expanded_changed(self, expanded: bool) -> None:  # noqa: FBT001
        self.icon = "-" if expanded else "+"


class DynamicPropertiesClock(Horizontal, CliveWidget):
    last_update_trigger = var(default=False)
    """A value that is used to trigger a re-rendering of the last update time."""

    def compose(self) -> ComposeResult:
        self.set_interval(1, self.__trigger_last_update)

        yield TitledLabel(
            "Block",
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self.__get_last_block,
        )
        yield TitledLabel(
            "Last update",
            obj_to_watch=self,
            attribute_name="last_update_trigger",
            callback=self.__get_last_update,
            id_="last-update",
        )

    async def __get_last_block(self) -> str:
        gdpo = await self.node.cached.dynamic_global_properties_or_none
        if gdpo is None:
            return NOT_AVAILABLE_LABEL

        block_num = gdpo.head_block_number
        block_time = gdpo.time.time()
        self.__trigger_last_update()
        return f"{block_num} ({block_time} UTC)"

    async def __get_last_update(self) -> str:
        gdpo = await self.node.cached.dynamic_global_properties_or_none
        if gdpo is None:
            return NOT_AVAILABLE_LABEL

        return humanize_natural_time(utc_now() - gdpo.time)

    def __trigger_last_update(self) -> None:
        self.last_update_trigger = not self.last_update_trigger


class Header(TextualHeader, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        self._header_title = HeaderTitle()
        super().__init__()
        self.__node_version_label = DynamicLabel(
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self.__get_node_version,
            id_="node-type-label",
        )

    def on_mount(self, event: Mount) -> None:
        # >>> start workaround for query_one(HeaderTitle) raising NoMatches error when title reactive is updated right
        # after pop_screen happens
        def set_title() -> None:
            self._header_title.text = self.screen_title

        def set_sub_title() -> None:
            self._header_title.sub_text = self.screen_sub_title

        event.prevent_default()

        self.watch(self.app, "title", set_title)
        self.watch(self.app, "sub_title", set_sub_title)
        self.watch(self.screen, "title", set_title)
        self.watch(self.screen, "sub_title", set_sub_title)
        # <<< end workaround

        self.watch(self.app, "header_expanded", self.header_expanded_changed)

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        with Horizontal(id="bar"):
            yield self.__node_version_label
            if not self.__is_in_onboarding_mode():
                yield TitledLabel(
                    "Profile",
                    obj_to_watch=self.world,
                    attribute_name="profile_data",
                    callback=self.__get_profile_name,
                    id_="profile-label",
                )
                with Center():
                    yield AlarmDisplay()

                async def mode_callback(app_state: AppState) -> str:
                    if app_state.is_unlocked:
                        self.add_class("-unlocked")
                        return "unlocked"
                    self.remove_class("-unlocked")
                    return "locked"

                yield TitledLabel(
                    "Mode",
                    obj_to_watch=self.world,
                    attribute_name="app_state",
                    callback=mode_callback,
                    id_="mode-label",
                )
            yield DynamicPropertiesClock()

        with Vertical(id="expandable"):
            yield self._header_title
            yield TitledLabel(
                "Node address",
                obj_to_watch=self.world,
                attribute_name="node",
                callback=self.__get_node_address,
                id_="node-address-label",
            )

    def on_click(self, event: events.Click) -> None:
        event.prevent_default()
        self.app.header_expanded = not self.app.header_expanded

    def header_expanded_changed(self, expanded: bool) -> None:  # noqa: FBT001
        self.add_class("-tall") if expanded else self.remove_class("-tall")

    @staticmethod
    def __get_node_address(node: Node) -> str:
        return str(node.address)

    @staticmethod
    def __get_profile_name(profile_data: ProfileData) -> str:
        return profile_data.name

    async def __get_node_version(self, node: Node) -> str:
        class_to_switch = "-not-mainnet"

        try:
            network_type = await node.cached.network_type
        except CommunicationError:
            network_type = "no connection"

        if network_type == "mainnet":
            self.__node_version_label.remove_class(class_to_switch)
        else:
            self.__node_version_label.add_class(class_to_switch)
        return network_type

    def __is_in_onboarding_mode(self) -> bool:
        return self.profile_data.name == ProfileData.ONBOARDING_PROFILE_NAME
