from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Checkbox, Footer, Header, Label


class ExampleApp(App):
    """
    https://textual.textualize.io.

    Najprostsza aplikacja w Textual która ma:
    1 mode - "_default"
    1 screen - id="_default"
    na tym ekranie 1 widget - Label

    - metoda `def compose` - w App, Screen, Widget (jest jeszcze def render)
    - modes
    - screen stacks
    - `python -m textual` (demo), `textual colors`, `textual keys`, `textual borders`, `textual console`, `textual-query-sandbox` (przez pip)
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"Hello, World: {self.current_mode=}, {self.screen=}")
        yield Label(f"Hello, World: {self.current_mode=}, {self.screen=}")
        yield Label(f"Hello, World: {self.current_mode=}, {self.screen=}", id="one")

        with Horizontal():
            yield Button("Button")
            yield Checkbox("Checkbox")

        yield Footer()


if __name__ == "__main__":
    ExampleApp().run()
