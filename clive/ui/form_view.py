from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from clive.ui.component import ConfigurableComponent

if TYPE_CHECKING:
    from clive.ui.views.form import Form  # noqa: F401


class FormView(ConfigurableComponent["Form"], ABC):
    """
    A view that is used to display in a multistep form.
    """
