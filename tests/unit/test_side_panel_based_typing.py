from __future__ import annotations

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Button, Label

from clive.ui.component import Component
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.components.side_panel_splitter import SidePanelSplitter
from clive.ui.views.side_pane_based import SidePanelBased


class MockMain(Component["SidePanelSplitter[MockMain, MockSide]"]):
    def mock_main_exclusive(self) -> None:
        print("mock_main_exclusive")

    def _create_container(self) -> Label:
        return Label("Main Component")


class MockSide(Component["SidePanelSplitter[MockMain, MockSide]"]):
    def mock_side_exclusive(self) -> None:
        print("mock_side_exclusive")

    def _create_container(self) -> Label:
        return Label("Side Component")


class MockMenu(ButtonsMenu["MockSidePanelBasedConcrete"]):
    def mock_menu_exclusive(self) -> None:
        print("mock_menu_exclusive")

    def _create_buttons(self) -> list[Button]:
        return [
            Button("Button 1"),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        return KeyBindings()


class MockSidePanelBasedConcrete(SidePanelBased[MockMain, MockSide, MockMenu]):
    def __init__(self) -> None:
        splitter = SidePanelSplitter(self)
        mock_main = MockMain(splitter)
        mock_side = MockSide(splitter)
        splitter.set_main_panel_first_time(mock_main)
        splitter.set_side_panel_first_time(mock_side)

        super().__init__(splitter, MockMenu(self))


def test_side_panel_based_types() -> None:
    m = MockSidePanelBasedConcrete()

    m.main_panel.mock_main_exclusive()  # should give no warning about missing attribute
    m.side_panel.mock_side_exclusive()  # should give no warning about missing attribute
    m.buttons.mock_menu_exclusive()  # should give no warning about missing attribute
