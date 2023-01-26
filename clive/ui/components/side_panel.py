from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from prompt_toolkit import HTML
from prompt_toolkit.layout import FormattedTextControl, HSplit, ScrollablePane, VSplit, Window
from prompt_toolkit.widgets import Frame, Label

from clive.app_status import app_status
from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.views.dashboard import Dashboard  # noqa: F401


class SidePanel(Component["Dashboard"]):
    def _create_container(self) -> HSplit:
        return HSplit(
            [
                self.__profile(),
                self.__mode(),
                Window(),
                self.__warnings(),
            ]
        )

    def __profile(self) -> VSplit:
        return VSplit(
            [
                Label("PROFILE:", style="bold"),
                Label(lambda: app_status.current_profile),
            ]
        )

    def __mode(self) -> VSplit:
        return VSplit(
            [
                Label("MODE:", style="bold"),
                Label(lambda: HTML("<red>ACTIVE</red>") if app_status.active_mode else HTML("<blue>INACTIVE</blue>")),
            ]
        )

    def __warnings(self) -> HSplit:
        return HSplit(
            [
                Label("\nWARNING MESSAGES:", style="class:red bold"),
                ScrollablePane(
                    HSplit(
                        [
                            *self.__get_warning_messages(),
                        ],
                        style="class:red",
                    )
                ),
            ]
        )

    def __get_warning_messages(self) -> Generator[Frame, None, None]:
        warnings = [
            "Your account will expire in 10 days if you don't vote for witness or proposal.",
            "The watched account: @gtg changed the owner authority.",
        ] * 6
        for idx, warning in enumerate(warnings):
            yield Frame(Window(FormattedTextControl(f"{idx + 1}. {warning}", focusable=True), wrap_lines=True))
