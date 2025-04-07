from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.events import Mount
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label


class FirstScreen(Screen):
    BINDINGS = [  # noqa: RUF012
        Binding("n", "go_to_second_screen", "Second screen"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"This is the first screen: {self.app.screen_stack=}", markup=False)
        yield Button("Go to second screen", id="go_to_second_screen")
        yield Footer()

    @on(Button.Pressed)
    def _go_to_second_screen(self) -> None:
        self.app.push_screen(SecondScreen())

    def action_go_to_second_screen(self) -> None:
        self.app.push_screen(SecondScreen())


class SecondScreen(Screen):
    BINDINGS = [  # noqa: RUF012
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"This is the second screen: {self.app.screen_stack=}", markup=False)
        yield Footer()


class ExampleApp(App):
    """
    Aplikacja z 2 ekranami - pierwszy pushowany na start, drugi w reakcji na binding/button.

    - custom screens
    - bindings (action)
    - messages (dekorator `@on` lub  metoda `def _on_...()`)
    """

    @on(Mount)
    def _push_first_screen(self) -> None:
    # def _on_mount(self) -> None:  # ekwiwalent
        self.push_screen(FirstScreen())


if __name__ == "__main__":
    ExampleApp().run()
