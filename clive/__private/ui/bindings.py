from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final, Union, get_type_hints

import inflection
from textual.binding import Binding
from toml import TomlDecodeError, dump, load

from clive.__private.settings import safe_settings
from clive.exceptions import BindingFileInvalidError

if TYPE_CHECKING:
    from textual.binding import Keymap


NestedDictStr = dict[str, Union[str, "NestedDictStr"]]

DEFAULT_BINDINGS_PATH: Final[Path] = Path(safe_settings.data_path) / "default_bindings.toml"
CUSTOM_BINDINGS_PATH: Final[Path] = Path(safe_settings.data_path) / "custom_bindings.toml"


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
        description_ = self.description or description
        return Binding(self.key, action, description_, show, key_display, priority, tooltip, self.id)


def custom_asdict(obj: object) -> NestedDictStr:
    """Convert dataclass containing CliveBinding to a dictionary."""
    if not is_dataclass(obj):
        raise TypeError("Not a dataclass")
    custom: NestedDictStr = {}
    for field_ in fields(obj):
        name = field_.name
        value = getattr(obj, name)
        if isinstance(value, CliveBinding):
            custom[name] = str(value)
        else:
            custom[name] = custom_asdict(value)
    return custom


@dataclass(frozen=True)
class Global:
    show_help: CliveBinding = field(default_factory=lambda: CliveBinding(id="show_help", key="f1,?"))
    hide_help: CliveBinding = field(default_factory=lambda: CliveBinding(id="hide_help", key="escape,q,f1,?"))
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
class Navigation:
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
    command_palette: CliveBinding = field(default_factory=lambda: CliveBinding(id="command_palette", key="ctrl+p"))
    glob: Global = field(default_factory=lambda: Global())
    dashboard: Dashboard = field(default_factory=lambda: Dashboard())
    transaction_summary: TransactionSummary = field(default_factory=lambda: TransactionSummary())
    operations: Operations = field(default_factory=lambda: Operations())
    navigation: Navigation = field(default_factory=lambda: Navigation())
    manage_key_aliases: ManageKeyAliases = field(default_factory=lambda: ManageKeyAliases())

    def dump_toml(self, dest: Path) -> None:
        data = custom_asdict(self)
        with dest.open("w") as f:
            dump(data, f)

    def get_formatted_global_bindings(self) -> str:
        content = ""
        for field_ in fields(self.glob):
            name = field_.name
            value = getattr(self.glob, name)
            content += value + "|" + name + "\n"
        return content

    @property
    def keymap(self) -> Keymap:
        keymap: dict[str, str] = {}

        def flatten(d: NestedDictStr) -> dict[str, str]:
            flattened: dict[str, str] = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    flattened.update(flatten(v))
                else:
                    d[str(k)] = str(v)
            return flattened

        all_bindings = custom_asdict(self)
        keymap = flatten(all_bindings)

        replacements = {"?": "question_mark"}
        for k, v in keymap.items():
            for old, new in replacements.items():
                keymap[k] = v.replace(old, new)
        return keymap

    def short_key(self, id_: str) -> str:
        all_keys = self.keymap[id_]
        first_key = all_keys.split(",")[0]
        return first_key.replace("ctrl+", "^")


CLIVE_PREDEFINED_BINDINGS: Final[CliveBindings] = CliveBindings()


def load_custom_bindings() -> CliveBindings:
    """Load bindings from the bindings.toml file. Throws exception if the file is not found or is invalid."""
    with CUSTOM_BINDINGS_PATH.open("r") as file:
        try:
            data = load(file)
            type_hints = get_type_hints(CliveBindings)
            if not set(data.keys()) <= set(type_hints.keys()):
                diff = set(data.keys()) - set(type_hints.keys())
                raise BindingFileInvalidError(f"{diff} are not valid bindings sections")
            parsed_inner_dataclass = {field: cls(**data[field]) for field, cls in type_hints.items() if field in data}
            return CliveBindings(**parsed_inner_dataclass)
        except TomlDecodeError as error:
            message = f"invalid toml format. {error}"
            raise BindingFileInvalidError(message) from error
        except TypeError as error:
            message = str(error)
            index = message.find("unexpected keyword argument")
            if index != -1:
                message = message[index:]
            raise BindingFileInvalidError(message) from error


def initialize_bindings_files() -> None:
    CLIVE_PREDEFINED_BINDINGS.dump_toml(DEFAULT_BINDINGS_PATH)
    if not CUSTOM_BINDINGS_PATH.exists():
        CUSTOM_BINDINGS_PATH.touch()
