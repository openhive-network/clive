"""Base class for binding sections."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, ClassVar

import inflection

from clive.__private.ui.bindings.clive_binding import CliveBinding
from clive.__private.ui.bindings.exceptions import BindingsDeserializeError

if TYPE_CHECKING:
    from collections.abc import Generator

    from clive.__private.ui.bindings.types import BindingSectionDict


@dataclass
class CliveBindingSection:
    """Base class for a group of related key bindings in a specific application section.

    This class serves as both a base class and a registry for binding sections. Each section
    corresponds to a different area of the application (App, Dashboard, Help, etc.).
    """

    ID: ClassVar[str] = ""
    _ID_TO_SUBCLASS: ClassVar[dict[str, type[CliveBindingSection]]] = {}

    def __init_subclass__(cls) -> None:
        if not cls.ID:
            cls.ID = inflection.underscore(cls.__name__)
        cls._ID_TO_SUBCLASS[cls.ID] = cls

    def __post_init__(self) -> None:
        for field_ in fields(self):
            value = getattr(self, field_.name)
            if not isinstance(value, CliveBinding):
                raise TypeError(f"Field '{field_.name}' must be CliveBinding, got {type(value).__name__}")

    def to_dict(self) -> BindingSectionDict:
        """Convert this binding section to a dictionary representation.

        Returns:
            Dictionary mapping binding IDs to key shortcuts
        """
        result: BindingSectionDict = {}
        for field_instance in self._bindings_fields():
            result[field_instance.id] = field_instance.key
        return result

    def _bindings_fields(self) -> Generator[CliveBinding]:
        """Yield all CliveBinding fields in this section."""
        for f in fields(self):
            field_value = getattr(self, f.name)
            if isinstance(field_value, CliveBinding):
                yield field_value

    def _update_keyboard_shortcut(self, binding_id: str, keyboard_shortcut: str) -> None:
        """Update a specific binding's key shortcut by ID.

        Args:
            binding_id: The ID of the binding to update
            keyboard_shortcut: The new key shortcut value

        Raises:
            BindingsDeserializeError: If binding_id doesn't match any binding in this section
        """
        for field_instance in self._bindings_fields():
            if field_instance.id == binding_id:
                field_instance.key = keyboard_shortcut
                return
        raise BindingsDeserializeError(f"Found unknown id `{binding_id}` when parsing bindings")

    @staticmethod
    def from_dict(section_name: str, section_dict: BindingSectionDict) -> CliveBindingSection:
        """Create a binding section instance from a dictionary representation.

        Args:
            section_name: The name of the section (must match a registered subclass ID)
            section_dict: Dictionary mapping binding IDs to key shortcuts

        Returns:
            A configured binding section instance

        Raises:
            BindingsDeserializeError: If section_name doesn't match any registered section
        """
        try:
            cls = CliveBindingSection._ID_TO_SUBCLASS[section_name]
        except KeyError as error:
            raise BindingsDeserializeError(f"Found unknown section `{section_name}` when parsing bindings") from error
        instance = cls()
        for id_, keyboard_shortcut in section_dict.items():
            instance._update_keyboard_shortcut(id_, keyboard_shortcut)
        return instance
