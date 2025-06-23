from __future__ import annotations

import stat
from dataclasses import dataclass, field, fields, is_dataclass
from typing import TYPE_CHECKING, Final, Union, get_type_hints

import inflection
import toml
from textual.binding import Binding

from clive.__private.settings import safe_settings
from clive.exceptions import BindingFileInvalidError, CliveError

if TYPE_CHECKING:
    from pathlib import Path

    from textual.binding import Keymap


NestedDictStr = dict[str, Union[str, "NestedDictStr"]]
CUSTOM_BINDINGS_INFO_MESSAGE: Final[str] = (
    "# This file contains custom key bindings for Clive.\n"
    "# You can define your custom bindings here, look at format in file `default_bindings.toml`.\n"
)
GLOBAL_BINDING_TABLE_PLACEHOLDER: Final[str] = "@GLOBAL_BINDING_TABLE_PLACEHOLDER@"


class BindingsDeserializeError(CliveError):
    """
    Raised when the bindings dictionary is loaded from TOML but cannot be used to create a CliveBindings.

    This might be due to incorrect TOML sections or fields.
    """


@dataclass
class CliveBinding:
    id: str
    key: str
    description: str | None = None
    """Will be determined from id if not given"""

    def __post_init__(self) -> None:
        if self.description is None:
            self.description = inflection.humanize(self.id)

    def __str__(self) -> str:
        return self.key

    def create(
        self,
        *,
        action: str,
        description: str = "",
        show: bool = True,
        key_display: str | None = None,
        priority: bool = False,
        tooltip: str = "",
    ) -> Binding:
        description_ = description or self.description or ""
        return Binding(self.key, action, description_, show, key_display, priority, tooltip, self.id)

    @property
    def key_short(self) -> str:
        return self.key.replace("ctrl+", "^")


@dataclass(frozen=True)
class Global:
    command_palette: CliveBinding = field(default_factory=lambda: CliveBinding(id="command_palette", key="ctrl+p"))
    show_help: CliveBinding = field(default_factory=lambda: CliveBinding(id="show_help", key="f1,?"))
    hide_help: CliveBinding = field(default_factory=lambda: CliveBinding(id="hide_help", key="escape,q,f1,?"))
    toggle_table_of_contents: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="toggle_table_of_contents", key="t")
    )
    dashboard: CliveBinding = field(default_factory=lambda: CliveBinding(id="dashboard", key="ctrl+d"))
    transaction_summary: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="transaction_summary", key="ctrl+t")
    )
    settings: CliveBinding = field(default_factory=lambda: CliveBinding(id="settings", key="ctrl+s"))
    clear_notifications: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="clear_notifications", key="ctrl+x")
    )
    quit: CliveBinding = field(default_factory=lambda: CliveBinding(id="quit", key="ctrl+q"))
    open_transaction_from_file: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="open_transaction_from_file", key="ctrl+o")
    )


@dataclass(frozen=True)
class Dashboard:
    operations: CliveBinding = field(default_factory=lambda: CliveBinding(id="operations", key="o"))
    switch_working_account: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="switch_working_account", key="w")
    )
    add_account: CliveBinding = field(default_factory=lambda: CliveBinding(id="add_account", key="a"))
    lock: CliveBinding = field(default_factory=lambda: CliveBinding(id="lock", key="ctrl+l"))


@dataclass(frozen=True)
class TransactionSummary:
    broadcast: CliveBinding = field(default_factory=lambda: CliveBinding(id="broadcast", key="b"))
    save_transaction_to_file: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="save_transaction_to_file", key="s")
    )
    update_metadata: CliveBinding = field(default_factory=lambda: CliveBinding(id="update_metadata", key="u"))


@dataclass(frozen=True)
class Operations:
    add_to_cart: CliveBinding = field(default_factory=lambda: CliveBinding(id="add_to_cart", key="a"))
    finalize_transaction: CliveBinding = field(default_factory=lambda: CliveBinding(id="finalize_transaction", key="f"))


@dataclass(frozen=True)
class FormNavigation:
    next_screen: CliveBinding = field(default_factory=lambda: CliveBinding(id="next_screen", key="ctrl+n"))
    previous_screen: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="previous_screen", key="ctrl+p,escape")
    )


@dataclass(frozen=True)
class ManageKeyAliases:
    new_alias: CliveBinding = field(default_factory=lambda: CliveBinding(id="new_alias", key="a"))
    load_from_file: CliveBinding = field(default_factory=lambda: CliveBinding(id="load_from_file", key="l"))


@dataclass(frozen=True)
class CliveBindings:
    glob: Global = field(default_factory=lambda: Global())
    dashboard: Dashboard = field(default_factory=lambda: Dashboard())
    transaction_summary: TransactionSummary = field(default_factory=lambda: TransactionSummary())
    operations: Operations = field(default_factory=lambda: Operations())
    form_navigation: FormNavigation = field(default_factory=lambda: FormNavigation())
    manage_key_aliases: ManageKeyAliases = field(default_factory=lambda: ManageKeyAliases())

    def dump_toml(self, dest: Path) -> None:
        if dest.exists():
            dest.chmod(stat.S_IWRITE)
        data = toml.dumps(self.to_dict())
        dest.write_text(data)
        dest.chmod(stat.S_IREAD)

    @staticmethod
    def from_dict(data: NestedDictStr) -> CliveBindings:
        def custom_from_dict[T](target_type: type[T], data: NestedDictStr) -> T:
            type_hints = get_type_hints(target_type)

            # Validate keys
            extra_keys = set(data.keys()) - set(type_hints.keys())
            if extra_keys:
                plural = "is not valid bindings section" if len(extra_keys) == 1 else "are not valid bindings sections"
                raise BindingsDeserializeError(f"{extra_keys} {plural}")

            # Build field dictionary
            field_dict = {}
            for field_name, field_cls in type_hints.items():
                if field_name in data:
                    dict_field_value = data[field_name]
                    field_dict[field_name] = (
                        CliveBinding(field_name, dict_field_value)
                        if isinstance(dict_field_value, str)
                        else custom_from_dict(field_cls, dict_field_value)
                    )

            return target_type(**field_dict)

        return custom_from_dict(CliveBindings, data)

    def get_formatted_global_bindings(self) -> str:
        content = ""
        for field_ in fields(self.glob):
            field_name = field_.name
            field_value = getattr(self.glob, field_name)
            content += field_value.key + "|" + field_.name + "\n"
        return content

    @property
    def keymap(self) -> Keymap:
        def flatten(nested: NestedDictStr) -> dict[str, str]:
            flattened: dict[str, str] = {}
            for key, value in nested.items():
                if isinstance(value, dict):
                    flattened.update(flatten(value))
                else:
                    flattened[str(key)] = str(value)
            return flattened

        all_bindings = self.to_dict()
        return flatten(all_bindings)

    @staticmethod
    def load_toml(path: Path) -> CliveBindings:
        try:
            data = toml.load(path)
        except toml.TomlDecodeError as error:
            message = f"invalid toml format. {error}"
            raise BindingFileInvalidError(message) from error

        try:
            return CliveBindings.from_dict(data)
        except BindingsDeserializeError as error:
            raise BindingFileInvalidError(str(error)) from error
        except TypeError as error:
            message = str(error)
            index = message.find("unexpected keyword argument")
            if index != -1:
                message = message[index:]
            raise BindingFileInvalidError(message) from error

    def to_dict(self) -> NestedDictStr:
        def custom_asdict(obj: object) -> NestedDictStr:
            assert is_dataclass(obj), "CliveBindings must be a dataclass containing other dataclasses"
            custom: NestedDictStr = {}
            for field_ in fields(obj):
                name = field_.name
                value = getattr(obj, name)
                if isinstance(value, CliveBinding):
                    custom[name] = str(value)
                else:
                    custom[name] = custom_asdict(value)
            return custom

        return custom_asdict(self)


CLIVE_PREDEFINED_BINDINGS: Final[CliveBindings] = CliveBindings()


def load_custom_bindings() -> CliveBindings:
    """Load bindings from the bindings.toml file. Throws exception if the file is not found or is invalid."""
    return CliveBindings.load_toml(safe_settings.custom_bindings_path)


def initialize_bindings_files() -> None:
    CLIVE_PREDEFINED_BINDINGS.dump_toml(safe_settings.default_bindings_path)
    custom_bindings_path = safe_settings.custom_bindings_path
    if not custom_bindings_path.exists():
        with custom_bindings_path.open("w") as f:
            f.write(CUSTOM_BINDINGS_INFO_MESSAGE)
