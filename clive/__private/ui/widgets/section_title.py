from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Static
from typing_extensions import Literal

SectionTitleVariant = Literal["default", "light", "red"]
"""The names of the valid section title variants."""


class SectionTitle(Static):
    DEFAULT_CSS = """
    SectionTitle {
        text-style: bold;
        background: $primary-darken-3;
        width: 1fr;
        height: 1;
        text-align: center;

        &.-light {
            background: $primary-lighten-3;
        }

        &.-red {
            background: $error-darken-3;
        }
    }
    """
    variant: SectionTitleVariant = reactive("default", init=False)  # type: ignore[assignment]

    def __init__(
        self, title: str, variant: SectionTitleVariant = "default", id_: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(title, id=id_, classes=classes)
        self.variant = variant

    def watch_variant(self, old_variant: str, variant: str) -> None:
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")
