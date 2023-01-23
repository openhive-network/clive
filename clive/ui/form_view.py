from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.views.form import Form  # noqa: F401


class FormView(Component["Form"], ABC):
    """
    A view that is used to display in a multistep form.
    """
