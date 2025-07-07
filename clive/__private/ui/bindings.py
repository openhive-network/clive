from __future__ import annotations

import stat
from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, ClassVar, Final, Self

import toml
from textual.binding import Binding

from clive.__private.core.formatters.case import underscore
from clive.__private.core.formatters.humanize import humanize_binding_id
from clive.__private.settings import safe_settings
from clive.exceptions import BindingFileInvalidError, CliveError

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from textual.binding import Keymap

type BindingID = str
type SectionID = str
type KeyboardShortcut = str

BindingSectionDict = dict[BindingID, KeyboardShortcut]
"""Mapping of binding IDs to their key shortcuts."""

BindingsDict = dict[SectionID, BindingSectionDict]
"""Mapping of section IDs to their binding dictionaries."""

_CUSTOM_BINDINGS_INFO_MESSAGE: Final[str] = (
    "# This file contains custom key bindings for Clive.\n"
    "# You can define your custom bindings here, look at format in file `default_bindings.toml`.\n"
)
_GLOBAL_BINDING_TABLE_PLACEHOLDER: Final[str] = "@GLOBAL_BINDING_TABLE_PLACEHOLDER@"


class BindingsDeserializeError(CliveError):
    """
    Raised when the bindings dictionary is loaded from TOML but cannot be used to create a CliveBindings.

    This might be due to incorrect TOML sections or fields.
    """


@dataclass
class CliveBinding:
    id: BindingID
    key: KeyboardShortcut
    description: str | None = None
    """Will be determined from id if not given"""

    def __post_init__(self) -> None:
        if self.description is None:
            self.description = humanize_binding_id(self.id)

    @property
    def bindings_display(self) -> str:
        return self._key_short

    @property
    def button_display(self) -> str:
        return self.bindings_display

    @property
    def _key_short(self) -> str:
        return self.key.replace("ctrl+", "^")

    def create(
        self,
        *,
        action: str | None = None,
        description: str = "",
        show: bool = True,
        key_display: str | None = None,
        priority: bool = False,
        tooltip: str = "",
    ) -> Binding:
        action_ = action if action is not None else self.id
        description_ = description or self.description or ""
        return Binding(self.key, action_, description_, show, key_display, priority, tooltip, self.id)


@dataclass
class CliveBindingSection:
    ID: ClassVar[SectionID] = ""
    _ID_TO_SUBCLASS: ClassVar[dict[SectionID, type[CliveBindingSection]]] = {}

    def __init_subclass__(cls) -> None:
        if not cls.ID:
            cls.ID = underscore(cls.__name__)
        cls._ID_TO_SUBCLASS[cls.ID] = cls

    def __post_init__(self) -> None:
        self._assert_all_fields_are_clive_binding()

    @staticmethod
    def from_dict(section_id: SectionID, section_dict: BindingSectionDict) -> CliveBindingSection:
        cls = CliveBindingSection._get_class_from_section_id(section_id)
        instance = cls()
        for id_, keyboard_shortcut in section_dict.items():
            instance._update_keyboard_shortcut(id_, keyboard_shortcut)
        return instance

    def to_dict(self) -> BindingSectionDict:
        result: BindingSectionDict = {}
        for field_instance in self._bindings_fields():
            result[field_instance.id] = field_instance.key
        return result

    def _assert_all_fields_are_clive_binding(self) -> None:
        for field_ in fields(self):
            instance = getattr(self, field_.name)
            assert isinstance(instance, CliveBinding), (
                f"Field '{field_.name}' must be CliveBinding, got {type(instance).__name__}"
            )

    def _bindings_fields(self) -> Generator[CliveBinding]:
        for field_ in fields(self):
            field_instance = getattr(self, field_.name)
            if isinstance(field_instance, CliveBinding):
                yield field_instance

    @staticmethod
    def _get_class_from_section_id(section_id: SectionID) -> type[CliveBindingSection]:
        try:
            return CliveBindingSection._ID_TO_SUBCLASS[section_id]
        except KeyError as error:
            raise BindingsDeserializeError(f"Found unknown section `{section_id}` when parsing bindings") from error

    def _update_keyboard_shortcut(self, binding_id: BindingID, keyboard_shortcut: KeyboardShortcut) -> None:
        for field_instance in self._bindings_fields():
            if field_instance.id == binding_id:
                field_instance.key = keyboard_shortcut
                return
        raise BindingsDeserializeError(f"Found unknown id `{binding_id}` when parsing bindings")


@dataclass
class App(CliveBindingSection):
    clear_notifications: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="clear_notifications", key="ctrl+x")
    )
    dashboard: CliveBinding = field(default_factory=lambda: CliveBinding(id="dashboard", key="ctrl+d"))
    load_transaction_from_file: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="load_transaction_from_file", key="ctrl+o")
    )
    settings: CliveBinding = field(default_factory=lambda: CliveBinding(id="settings", key="ctrl+s"))
    transaction_summary: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="transaction_summary", key="ctrl+t")
    )
    quit: CliveBinding = field(default_factory=lambda: CliveBinding(id="quit", key="ctrl+q"))


@dataclass
class Dashboard(CliveBindingSection):
    operations: CliveBinding = field(default_factory=lambda: CliveBinding(id="operations", key="o"))
    switch_working_account: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="switch_working_account", key="w")
    )
    add_account: CliveBinding = field(default_factory=lambda: CliveBinding(id="add_account", key="a"))
    lock: CliveBinding = field(default_factory=lambda: CliveBinding(id="lock", key="ctrl+l"))


@dataclass
class FormNavigation(CliveBindingSection):
    next_screen: CliveBinding = field(default_factory=lambda: CliveBinding(id="next_screen", key="ctrl+n"))
    previous_screen: CliveBinding = field(default_factory=lambda: CliveBinding(id="previous_screen", key="ctrl+b"))


@dataclass
class Help(CliveBindingSection):
    toggle_help: CliveBinding = field(default_factory=lambda: CliveBinding(id="toggle_help", key="f1,?"))
    toggle_table_of_contents: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="toggle_table_of_contents", key="t")
    )


@dataclass
class ManageKeyAliases(CliveBindingSection):
    add_new_alias: CliveBinding = field(default_factory=lambda: CliveBinding(id="add_new_alias", key="a"))
    load_from_file: CliveBinding = field(default_factory=lambda: CliveBinding(id="load_from_file", key="l"))


@dataclass
class Operations(CliveBindingSection):
    add_to_cart: CliveBinding = field(default_factory=lambda: CliveBinding(id="add_to_cart", key="a"))
    finalize_transaction: CliveBinding = field(default_factory=lambda: CliveBinding(id="finalize_transaction", key="f"))
    witness_show_details: CliveBinding = field(default_factory=lambda: CliveBinding(id="wtness_show_details", key="d"))


@dataclass
class TransactionSummary(CliveBindingSection):
    broadcast: CliveBinding = field(default_factory=lambda: CliveBinding(id="broadcast", key="b"))
    save_transaction_to_file: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="save_transaction_to_file", key="s")
    )
    update_metadata: CliveBinding = field(default_factory=lambda: CliveBinding(id="update_metadata", key="u"))


@dataclass
class CliveBindings:
    app: App = field(default_factory=lambda: App())
    dashboard: Dashboard = field(default_factory=lambda: Dashboard())
    form_navigation: FormNavigation = field(default_factory=lambda: FormNavigation())
    help: Help = field(default_factory=lambda: Help())
    manage_key_aliases: ManageKeyAliases = field(default_factory=lambda: ManageKeyAliases())
    operations: Operations = field(default_factory=lambda: Operations())
    transaction_summary: TransactionSummary = field(default_factory=lambda: TransactionSummary())

    def __post_init__(self) -> None:
        self._assert_all_fields_are_sections()

    def dump_toml(self, dest: Path) -> None:
        if dest.exists():
            dest.chmod(stat.S_IWRITE)
        data = toml.dumps(self.to_dict())
        dest.write_text(data)
        dest.chmod(stat.S_IREAD)

    @classmethod
    def load_toml(cls, path: Path) -> Self:
        try:
            data = toml.load(path)
        except toml.TomlDecodeError as error:
            message = f"invalid toml format. {error}"
            raise BindingFileInvalidError(message) from error

        try:
            return cls.from_dict(data)
        except BindingsDeserializeError as error:
            raise BindingFileInvalidError(str(error)) from error

    def to_dict(self) -> BindingsDict:
        result: BindingsDict = {}
        for _, field_instance in self._binding_section_fields():
            result[field_instance.ID] = field_instance.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: BindingsDict) -> Self:
        instance = cls()
        for section_id, section_dict in data.items():
            section_instance = CliveBindingSection.from_dict(section_id, section_dict)
            instance._update_section(section_id, section_instance)
        return instance

    def get_formatted_global_bindings(self, content: str) -> str:
        return content.replace(_GLOBAL_BINDING_TABLE_PLACEHOLDER, self._get_global_bindings_table())

    @property
    def keymap(self) -> Keymap:
        def flatten(bindings_dict: BindingsDict) -> Keymap:
            flattened = {}
            for section_dict in bindings_dict.values():
                flattened.update(section_dict)
            return flattened

        all_bindings = self.to_dict()
        return flatten(all_bindings)

    def _assert_all_fields_are_sections(self) -> None:
        for field_ in fields(self):
            instance = getattr(self, field_.name)
            assert isinstance(instance, CliveBindingSection), (
                f"Field '{field_.name}' must be CliveBindingSection, got {type(instance).__name__}"
            )

    def _binding_section_fields(self) -> Generator[tuple[str, CliveBindingSection]]:
        for field_ in fields(self):
            instance = getattr(self, field_.name)
            if isinstance(instance, CliveBindingSection):
                yield field_.name, instance

    def _get_global_bindings_table(self) -> str:
        table = ""
        table += "| Binding  | Action                    |\n"
        table += "|:--------:|---------------------------|\n"

        for field_ in fields(self.app):
            field_name = field_.name
            instance = getattr(self.app, field_name)
            table += instance.key + "|" + field_.name + "\n"
        return table

    def _update_section(self, section_id: SectionID, section_instance: CliveBindingSection) -> None:
        for field_name, field_instance in self._binding_section_fields():
            if section_id == field_instance.ID:
                setattr(self, field_name, section_instance)
                return


CLIVE_PREDEFINED_BINDINGS: Final[CliveBindings] = CliveBindings()


def load_custom_bindings() -> CliveBindings:
    """Load bindings from the bindings.toml file. Throws exception if the file is not found or is invalid."""
    return CliveBindings.load_toml(safe_settings.custom_bindings_path)


def initialize_bindings_files() -> None:
    CLIVE_PREDEFINED_BINDINGS.dump_toml(safe_settings.default_bindings_path)
    custom_bindings_path = safe_settings.custom_bindings_path
    if not custom_bindings_path.exists():
        custom_bindings_path.write_text(_CUSTOM_BINDINGS_INFO_MESSAGE)
