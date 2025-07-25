from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.formatters.case import underscore
from clive.__private.ui.bindings.clive_binding import CliveBinding
from clive.__private.ui.bindings.exceptions import BindingsDeserializeError

if TYPE_CHECKING:
    from collections.abc import Generator

    from clive.__private.ui.bindings.types import BindingID, BindingSectionDict, KeyboardShortcut, SectionID


@dataclass
class CliveBindingSection:
    """
    This class is intended to be subclassed for each section of bindings.

    Section id is determined from the class name by default but can be overridden by setting the `ID` class variable.

    Attributes:
        ID: The unique ID of the section. Will be determined from the class name if not overridden.
    """

    ID: ClassVar[SectionID] = ""
    _ID_TO_SUBCLASS: ClassVar[dict[SectionID, type[CliveBindingSection]]] = {}

    def __init_subclass__(cls) -> None:
        if not cls.ID:
            cls.ID = underscore(cls.__name__)
        cls._ID_TO_SUBCLASS[cls.ID] = cls

    def __post_init__(self) -> None:
        self._assert_all_fields_are_clive_binding()

    @classmethod
    def from_dict(cls, section_id: SectionID, section_dict: BindingSectionDict) -> CliveBindingSection:
        """Create a binding section instance from a dictionary representation.

        Args:
            section_id: The name of the section (must match a registered subclass ID)
            section_dict: Dictionary mapping binding IDs to key shortcuts

        Returns:
            A configured binding section instance

        Raises:
            BindingsDeserializeError: If section_name doesn't match any registered section
        """
        subclass = cls._get_class_from_section_id(section_id)
        instance = subclass()
        for id_, keyboard_shortcut in section_dict.items():
            instance._update_keyboard_shortcut(id_, keyboard_shortcut)
        return instance

    def to_dict(self) -> BindingSectionDict:
        """Convert this binding section to a dictionary representation.

        Returns:
            Dictionary mapping binding IDs to key shortcuts
        """
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
        """
        Get all the CliveBinding fields from this section.

        Yields:
            Each field that is an instance of CliveBinding.
        """
        for field_ in fields(self):
            field_instance = getattr(self, field_.name)
            if isinstance(field_instance, CliveBinding):
                yield field_instance

    @classmethod
    def _get_class_from_section_id(cls, section_id: SectionID) -> type[CliveBindingSection]:
        try:
            return cls._ID_TO_SUBCLASS[section_id]
        except KeyError as error:
            raise BindingsDeserializeError(f"Found unknown section `{section_id}` when parsing bindings") from error

    def _update_keyboard_shortcut(self, binding_id: BindingID, keyboard_shortcut: KeyboardShortcut) -> None:
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
