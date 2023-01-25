from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from clive.ui.views.form import Form

if TYPE_CHECKING:
    from clive.ui.form_view import FormView


class FormViewConvertible(ABC):
    """
    FormViewConvertible classes are views can be converted to FormView
    """

    @staticmethod
    @abstractmethod
    def convert_to_form_view(parent: Form) -> FormView:
        """
        Convert self to subclass of FormView class

        Returns:
            FormView: constructed child class of FormView
        """
