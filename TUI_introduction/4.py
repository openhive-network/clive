from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Label


class SomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Label("Hello from SomeScreen")

    async def on_mount(self) -> None:
        await asyncio.sleep(2)


class ExampleApp(App):
    """
    Aplikacja z metodą "await me maybe".

    - AwaitMount, AwaitRemove, AwaitComplete (po cichu zadzieja sie pozniej)
    """

    BINDINGS = [  # noqa: RUF012
        ("t", "test", "Test"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()

    def action_test(self) -> None:
        self.push_screen(SomeScreen())  # należy awaitować
        self.screen.query_exactly_one(Label).styles.border = ("heavy", "red")


if __name__ == "__main__":
    ExampleApp().run()
