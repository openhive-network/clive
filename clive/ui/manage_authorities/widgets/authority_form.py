from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import Button, DirectoryTree, Input, Label, Static, Switch

from clive.storage.mock_database import PrivateKey
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.notification import Notification
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ModeSwitchContainer(Horizontal):
    def compose(self) -> ComposeResult:
        yield Switch()
        yield Static("Toggle mode")


class ButtonSave(Button):
    def __init__(self) -> None:
        super().__init__("💾 Save", id="save-button")


class ButtonsContainer(Horizontal):
    """Container for buttons"""


class Body(Container):
    """Container for body"""


class AuthorityNameContainer(Horizontal):
    """Container for authority name label and input"""


class AuthorityNameLabel(Label):
    """Label for authority name"""


class AuthorityNameInput(Input):
    """Input for authority name"""


class SubTitle(Static):
    pass


class ManualFilePath(Static):
    def __init__(self) -> None:
        super().__init__(classes="-hidden")
        self.input = Input(placeholder="e.g.: /home/me/my-active-key")

    def compose(self) -> ComposeResult:
        yield Static("Please manually enter the path to the authority file:")
        yield self.input


class TreeFileSelector(Container):
    def __init__(self) -> None:
        super().__init__()
        self.directory_tree = DirectoryTree(str(Path.home()))

    def compose(self) -> ComposeResult:
        yield Static("Please select the authority file:")
        yield self.directory_tree


class AuthorityForm(BaseScreen):
    BINDINGS = [("f10", "save", "Save")]

    class Saved(Message, bubble=True):
        """Emitted when user Saves the form"""

        def __init__(self, sender: AuthorityForm, private_key: PrivateKey) -> None:
            self.private_key = private_key
            super().__init__(sender)

    class AuthoritiesChanged(Message):
        """Emitted when authorities have been changed"""

    def __init__(self) -> None:
        super().__init__()

        self.__authority_name_input = AuthorityNameInput(self._default_authority_name(), "e.g. My active key")
        self.__manual_file_path = ManualFilePath()
        self.__tree_file_selector = TreeFileSelector()

    def on_mount(self) -> None:
        if self._default_file_path():
            self.__manual_file_path.input.value = self._default_file_path()
            self.query_one(Switch).toggle()

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle(self._title())
            if self._subtitle():
                yield SubTitle(self._subtitle())
            with Body():
                with AuthorityNameContainer():
                    yield AuthorityNameLabel("Key alias:")
                    yield self.__authority_name_input
                yield Static()
                yield ModeSwitchContainer()
                yield Static()
                yield self.__manual_file_path
                yield self.__tree_file_selector
                yield Static()
                yield ButtonSave()
                yield Static()

    def action_save(self) -> None:
        if not self.__is_valid():
            Notification("Failed the validation process! Could not continue", category="error").show()
            return

        file_path = self.__get_file_path()
        assert file_path  # it was validated before

        private_key = PrivateKey.from_file(self.__authority_name_input.value, file_path)
        self.app.post_message_to_everyone(self.Saved(self, private_key))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-button":
            self.action_save()

    def on_switch_changed(self) -> None:
        self.__manual_file_path.toggle_class("-hidden")
        self.__tree_file_selector.toggle_class("-hidden")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.__manual_file_path.input.value = event.path

    def _title(self) -> str:
        return ""

    def _subtitle(self) -> str:
        return ""

    def _default_authority_name(self) -> str:
        return ""

    def _default_file_path(self) -> str:
        return ""

    def __get_file_path(self) -> Path | None:
        path = Path(self.__manual_file_path.input.value)
        if not path.is_file():
            return None
        return path

    def __is_valid(self) -> bool:
        return bool(self.__get_file_path()) and bool(self.__authority_name_input.value)
