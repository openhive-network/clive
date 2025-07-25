from __future__ import annotations

import stat
from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, Final, Self

import toml

from clive.__private.settings import safe_settings
from clive.__private.ui.bindings.clive_binding_section import CliveBindingSection
from clive.__private.ui.bindings.exceptions import BindingFileInvalidError, BindingsDeserializeError
from clive.__private.ui.bindings.sections import (
    App,
    Dashboard,
    FormNavigation,
    Help,
    ManageKeyAliases,
    Operations,
    TransactionSummary,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from textual.binding import Keymap

    from clive.__private.ui.bindings.types import BindingsDict, SectionID


_CUSTOM_BINDINGS_INFO_MESSAGE: Final[str] = (
    "# This file contains custom key bindings for Clive.\n"
    "# You can define your custom bindings here, look at format in file `default_bindings.toml`.\n"
)
_GLOBAL_BINDING_TABLE_PLACEHOLDER: Final[str] = "@GLOBAL_BINDING_TABLE_PLACEHOLDER@"


@dataclass
class CliveBindings:
    """
    Object that can be converted to and from dictionary and in consequence toml format.

    Contains sections with key bindings for different parts of the application.
    Each section is a `CliveBindingSection` instance, which contains `CliveBinding` instances.
    """

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
        """Serialize bindings to a TOML file.

        Args:
            dest: Path where the TOML file will be written
        """
        if dest.exists():
            dest.chmod(stat.S_IWRITE)
        data = toml.dumps(self.to_dict())
        dest.write_text(data)
        dest.chmod(stat.S_IREAD)

    @classmethod
    def load_toml(cls, path: Path) -> Self:
        """Load bindings from a TOML file.

        Args:
            path: Path to the TOML file to load from

        Returns:
            This instance populated with data from the TOML file

        Raises:
            BindingFileInvalidError: If the TOML file is invalid or contains invalid bindings
        """
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
        """Convert all binding sections to a nested dictionary representation.

        Returns:
            Dictionary mapping section IDs to their binding dictionaries
        """
        result: BindingsDict = {}
        for _, field_instance in self._binding_section_fields():
            result[field_instance.ID] = field_instance.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: BindingsDict) -> Self:
        """Create a new instance from a nested dictionary representation.

        Args:
            data: Dictionary mapping section IDs to their binding dictionaries

        Returns:
            The instance populated with data from the dictionary
        """
        instance = cls()
        for section_id, section_dict in data.items():
            section_instance = CliveBindingSection.from_dict(section_id, section_dict)
            instance._update_section(section_id, section_instance)
        return instance

    def get_formatted_global_bindings(self, content: str) -> str:
        """Replace placeholder in content with a formatted global bindings table.

        Args:
            content: A content (text) containing the placeholder to replace

        Returns:
            A content (text) with placeholder replaced with binding table
        """
        return content.replace(_GLOBAL_BINDING_TABLE_PLACEHOLDER, self._get_global_bindings_table())

    @property
    def keymap(self) -> Keymap:
        """Generate a flat keymap from all binding sections.

        Returns:
            A flattened dictionary mapping key shortcuts to their binding IDs
        """

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
    """Load bindings from the TOML file.

    Raises:
        FileNotFoundError: If the file is not found.
        BindingFileInvalidError: If the file with bindings has an invalid format.

    Returns:
        An object containing mapping of BindingID to KeyboardShortcut.
    """
    return CliveBindings.load_toml(safe_settings.custom_bindings_path)


def initialize_bindings_files() -> None:
    """Initialize binding configuration files.

    Notice:
        This function performs two actions:

            1. Writes the default bindings to the default bindings path (overwriting if it exists)
            2. Creates a custom bindings template file if it doesn't already exist
    """
    CLIVE_PREDEFINED_BINDINGS.dump_toml(safe_settings.default_bindings_path)
    custom_bindings_path = safe_settings.custom_bindings_path
    if not custom_bindings_path.exists():
        custom_bindings_path.write_text(_CUSTOM_BINDINGS_INFO_MESSAGE)
