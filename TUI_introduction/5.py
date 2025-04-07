from __future__ import annotations

from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import Button, Label, ProgressBar


class Counter(Widget):
    DEFAULT_CSS = "Counter { height: auto; }"
    counter = var(0)

    def compose(self) -> ComposeResult:
        yield Label()
        yield Button("+10")

    def on_button_pressed(self) -> None:
        self.counter += 10

    def watch_counter(self, counter_value: int) -> None:
        self.query_one(Label).update(str(counter_value))


class WatchApp(App):
    """
    Aplikacja z reactive attributes.

    - reactive (smart refresh, recompose) , var
    - self.watch
    - profile_reactive, node_reactive, DataProvider
    - mutate_reactive, trigger_profile_watchers
    """

    def compose(self) -> ComposeResult:
        yield Counter()
        yield ProgressBar(total=100, show_eta=False)

    def on_mount(self) -> None:
        def update_progress(counter_value: int) -> None:
            self.query_one(ProgressBar).update(progress=counter_value)

        self.watch(self.query_one(Counter), "counter", update_progress)


if __name__ == "__main__":
    WatchApp().run()
