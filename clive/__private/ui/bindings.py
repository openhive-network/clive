from __future__ import annotations

from dataclasses import asdict, dataclass, field, make_dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final, get_type_hints

from toml import TomlDecodeError

from clive.__private.core.constants.tui import (
    dashboard_bindings,
    global_bindings,
    navigation_bindings,
    operations_common_bindings,
    transaction_summary_bindings,
)
from clive.__private.core.types import BindingIdKey
from clive.__private.settings import safe_settings
from clive.exceptions import BindingFileInvalidError

if TYPE_CHECKING:
    from types import ModuleType

    from textual.binding import Keymap


def _make_dataclass_fields(constants_module: ModuleType) -> list[tuple[str, type, str]]:
    """Create fields for dataclass with bindings."""
    bindings: list[BindingIdKey] = [
        getattr(constants_module, name)
        for name in dir(constants_module)
        if isinstance(getattr(constants_module, name), BindingIdKey)
    ]
    return [(binding.id, str, binding.key) for binding in bindings]


Dashboard = make_dataclass(
    "Dashboard",
    _make_dataclass_fields(dashboard_bindings),
    frozen=True,
    kw_only=True,
)


GlobalBindings = make_dataclass(
    "GlobalBindings",
    _make_dataclass_fields(global_bindings),
    frozen=True,
    kw_only=True,
)


Navigation = make_dataclass(
    "Navigation",
    _make_dataclass_fields(navigation_bindings),
    frozen=True,
    kw_only=True,
)


OperationsCommon = make_dataclass(
    "OperationsCommon",
    _make_dataclass_fields(operations_common_bindings),
    frozen=True,
    kw_only=True,
)


TransactionSummary = make_dataclass(
    "TransactionSummary",
    _make_dataclass_fields(transaction_summary_bindings),
    frozen=True,
    kw_only=True,
)


@dataclass(frozen=True)
class Bindings:
    dashboard: Dashboard = field(default_factory=Dashboard)  # type: ignore [valid-type]
    global_bindings: GlobalBindings = field(default_factory=GlobalBindings)  # type: ignore [valid-type]
    navigation: Navigation = field(default_factory=Navigation)  # type: ignore [valid-type]
    operations_common: OperationsCommon = field(default_factory=OperationsCommon)  # type: ignore [valid-type]
    transaction_summary: TransactionSummary = field(default_factory=TransactionSummary)  # type: ignore [valid-type]

    def dump_toml(self, dest: Path) -> None:
        import toml

        data = asdict(self)
        with dest.open("x") as f:
            toml.dump(data, f)

    @property
    def keymap(self) -> Keymap:
        keymap: dict[str, str] = {}
        for keymap_part in asdict(self).values():
            keymap.update(keymap_part)
        replacements = {"?": "question_mark"}
        for k, v in keymap.items():
            for old, new in replacements.items():
                keymap[k] = v.replace(old, new)
        return keymap

    def short_key(self, id_: str) -> str:
        all_keys = self.keymap[id_]
        first_key = all_keys.split(",")[0]
        return first_key.replace("ctrl+", "^")

    def get_formatted_global_bindings(self) -> str:
        content = ""
        for k, v in asdict(self.global_bindings).items():
            content += str(v) + "|" + str(k) + "\n"
        return content


DEFAULT_BINDINGS: Final[Bindings] = Bindings()


def load_bindings() -> Bindings:
    """Load bindings from the bindings.toml file. Throws exception if the file is not found or is invalid."""
    import toml

    bindings_path = Path(safe_settings.data_path) / "bindings.toml"
    with bindings_path.open("r") as file:
        try:
            data = toml.load(file)
            type_hints = get_type_hints(Bindings)
            parsed_inner_dataclass = {field: cls(**data[field]) for field, cls in type_hints.items() if field in data}
            return Bindings(**parsed_inner_dataclass)
        except TomlDecodeError as error:
            message = str(error)
            raise BindingFileInvalidError(message) from error
        except TypeError as error:
            message = str(error)
            index = message.find("unexpected keyword argument")
            if index != -1:
                message = message[index:]
            raise BindingFileInvalidError(message) from error


def initialize_bindings_file() -> None:
    bindings_path = Path(safe_settings.data_path) / "bindings.toml"
    if not bindings_path.is_file():
        DEFAULT_BINDINGS.dump_toml(bindings_path)
