from __future__ import annotations

from time import monotonic

from textual import on
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header


class TimeDisplay(Digits):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")

    @on(Button.Pressed)
    def _handle_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS = """
    Stopwatch {
        background: $boost;
        height: 5;
        margin: 1;
        min-width: 50;
        padding: 1;
    }

    TimeDisplay {
        text-align: center;
        color: $foreground-muted;
        height: 3;
    }

    Button {
        width: 16;
    }

    #start {
        dock: left;
    }

    #stop {
        dock: left;
        display: none;
    }

    #reset {
        dock: right;
    }

    .started {
        background: $success-muted;
        color: $text;
    }

    .started TimeDisplay {
        color: $foreground;
    }

    .started #start {
        display: none
    }

    .started #stop {
        display: block
    }

    .started #reset {
        visibility: hidden
    }
"""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with VerticalScroll():
            for _ in range(3):
                yield Stopwatch()

        yield Footer()


if __name__ == "__main__":
    StopwatchApp().run()
