from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.widgets import TextArea

from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.views.dashboard import Dashboard  # noqa: F401


class RightComponent(Component["Dashboard"]):
    def _create_container(self) -> TextArea:
        return TextArea(
            text="RIGHT COMPONENT",
            style="class:primary",
            focus_on_click=True,
        )
