from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class BindingButton(CliveButton):
    """Class to display button with label of binding description and key."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that BindingButton button was pressed."""

    def __init__(
        self,
        binding_key: str,
        bindings_list: list[Binding],
        id_: str | None = None,
    ) -> None:
        """
        Initialize the BindingButton.

        Args:
        ----
        binding_key: binding to be displayed on button label. Should be the same as in bindings list.
        bindings_list: list of bindings in class, should be self.BINDINGS or ScreenClassName.BINDINGS.
        id_: button id.
        """
        binding_key = binding_key.lower()
        button_label = ""

        for binding in bindings_list:
            assert isinstance(
                binding, Binding
            ), f"{self.__class__.__name__} should be used only with `Binding` class! Got {type(binding)}"
            if binding.key == binding_key:
                button_label = f"{binding.description} ({binding_key.upper()})"
                break

        assert bool(button_label), f"Key binding {binding_key} not found in the {bindings_list}"
        super().__init__(label=button_label, variant="success", id_=id_)


class BindingOneLineButton(OneLineButton, BindingButton):
    class Pressed(BindingButton.Pressed):
        """Used to identify exactly that BindingOneLineButton was pressed."""
