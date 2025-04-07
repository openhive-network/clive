from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Label


class SomeWidget(Widget, can_focus=True):
    DEFAULT_CSS = """
    SomeWidget {
        background: $primary-darken-1;
        border: solid red;
        height: auto;
        layout: horizontal;
        align: center middle;

        Label {
            height: 3;
            align: center middle;

            &:hover {
                background: green;
            }
        }

        Button {
            &:focus {
                background: orange;
            }
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Press me: ")
        yield Button("Click!")


class ExampleApp(App):
    """
    Aplikacja z custom widget skomponowany z dwóch innych.

    - CSS (inline i w pliku) - mamy w clive metody get_css_from_relative_path i get_relative_css_path
    - live editing jesli jest w pliku
    - odwołanie po typie widgetu (Label, Button), po klasie, po id, descendant (zagniezdzony) i child `>` - (bezposredni child)
    - Variables
    - Pseudoselektory
    - 1fr, auto (zamiast stałej wartosci)
    """

    def compose(self) -> ComposeResult:
        yield SomeWidget()


if __name__ == "__main__":
    ExampleApp().run()
