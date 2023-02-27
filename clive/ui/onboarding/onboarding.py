from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import var
from textual.widgets import Footer, Static

from clive.ui.login.login import Login
from clive.ui.registration.registration import Registration
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.select import Select


class Onboarding(BaseScreen):
    BINDINGS = [
        Binding("p", "previous_screen", "Previous screen"),
        Binding("n", "next_screen", "Next screen"),
    ]

    SCREENS = [
        Registration(),
        Login(),
    ]


    current_screen_index = var(0)

    def on_mount(self):
        self.__mount_current_screen()

    def create_main_panel(self) -> ComposeResult:
        self.stepper = Static(f"Screen {self.current_screen_index + 1} of {len(self.SCREENS)}", id="stepper")
        yield self.stepper

    def action_next_screen(self):
        if self.current_screen_index >= len(self.SCREENS) - 1:
            return

        self.current_screen_index += 1
        self.__mount_current_screen()

    def action_previous_screen(self):
        if self.current_screen_index <= 0:
            return

        self.current_screen_index -= 1
        self.__mount_current_screen()

    def __mount_current_screen(self):
        self.__remove_mounted_widgets()
        self.mount_all(self.SCREENS[self.current_screen_index].as_form())
        self.stepper.update(f"Screen {self.current_screen_index + 1} of {len(self.SCREENS)}")

    def __remove_mounted_widgets(self):
        for widget in self.screen.query("*"):

            if isinstance(widget, Footer):
                continue

            if widget.id == "stepper":
                continue
            widget.remove()
