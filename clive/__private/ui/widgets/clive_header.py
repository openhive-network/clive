from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.reactive import var
from textual.widgets import Header, Static
from textual.widgets._header import HeaderIcon as TextualHeaderIcon
from textual.widgets._header import HeaderTitle

from clive.__private.core.formatters.data_labels import NOT_AVAILABLE_LABEL
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


class HeaderIcon(TextualHeaderIcon, CliveWidget):
    DEFAULT_CSS = """
    HeaderIcon:hover {
        background: rgba(0, 0, 0 , 0.2);
    }
    """

    def __init__(self) -> None:
        super().__init__(id="icon")
        self.tooltip = "Toggle header details"

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.header_expanded_changed)

    def header_expanded_changed(self, expanded: bool) -> None:  # noqa: FBT001
        self.icon = "-" if expanded else "+"

    def on_click(self) -> None:  # type: ignore[override]
        self.app.header_expanded = not self.app.header_expanded


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

    async def __get_last_block(self) -> str:
        gdpo = await self.node.cached.dynamic_global_properties_or_none
        if gdpo is None:
            return NOT_AVAILABLE_LABEL

        block_num = gdpo.head_block_number
        block_time = gdpo.time.time()
        self.__trigger_last_update()
        return f"{block_num} ({block_time} UTC)"

    def __trigger_last_update(self) -> None:
        self.last_update_trigger = not self.last_update_trigger


class CliveHeader(Header, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        self._header_title = HeaderTitle()
        super().__init__()
        self.__node_version = DynamicLabel(
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self.__get_node_version,
            id_="node-type",
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
            if not self.__is_in_onboarding_mode():
                yield DynamicLabel(
                    obj_to_watch=self.world,
                    attribute_name="profile_data",
                    callback=self.__get_profile_name,
                    id_="profile-name",
                )
                yield Static("/", id="separator")
                yield DynamicLabel(
                    obj_to_watch=self.world,
                    attribute_name="profile_data",
                    callback=self._get_working_account_name,
                    id_="working-account-name",
                )
                yield AlarmDisplay()

                async def mode_callback(app_state: AppState) -> str:
                    if app_state.is_unlocked:
                        self.add_class("-unlocked")
                        return "unlocked"
                    self.remove_class("-unlocked")
                    return "locked"

                yield DynamicLabel(
                    obj_to_watch=self.world,
                    attribute_name="app_state",
                    callback=mode_callback,
                    id_="mode-label",
                )

        with Horizontal(id="expandable"):
            yield DynamicPropertiesClock()
            yield self._header_title
            yield DynamicLabel(
                obj_to_watch=self.world,
                attribute_name="node",
                callback=self.__get_node_address,
                id_="node-address-label",
            )
            yield self.__node_version

    def header_expanded_changed(self, expanded: bool) -> None:  # noqa: FBT001
        self.add_class("-tall") if expanded else self.remove_class("-tall")

    def _on_click(self, event: events.Click) -> None:  # type: ignore[override]
        """
        Override this method to prevent expanding header on click.

        Default behavior of the textual header is to expand on click.
        We do not want behavior like that, so we had to override the `_on_click` method.
        """
        event.prevent_default()

    @staticmethod
    def __get_node_address(node: Node) -> str:
        return str(node.address)

    @staticmethod
    def __get_profile_name(profile_data: ProfileData) -> str:
        return profile_data.name

    @staticmethod
    def _get_working_account_name(profile_data: ProfileData) -> str:
        return f"@{profile_data.working_account.name}" if profile_data.is_working_account_set() else "-"

    async def __get_node_version(self, node: Node) -> str:
        class_to_switch = "-not-mainnet"

        try:
            network_type = await node.cached.network_type
        except CommunicationError:
            network_type = "no connection"

        if network_type == "mainnet":
            self.__node_version.remove_class(class_to_switch)
        else:
            self.__node_version.add_class(class_to_switch)
        return f"({network_type})"

    def __is_in_onboarding_mode(self) -> bool:
        from clive.__private.ui.onboarding.onboarding import Onboarding

        return self.profile_data.name == Onboarding.ONBOARDING_PROFILE_NAME
