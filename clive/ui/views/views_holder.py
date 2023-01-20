from __future__ import annotations

from typing import TYPE_CHECKING

from clive.ui.view_manager import view_manager
from clive.ui.views.dashboard import Dashboard
from clive.ui.views.form import Form
from clive.ui.views.welcome import Welcome

if TYPE_CHECKING:
    from clive.ui.view import View

views: dict[str, View] = {"welcome": Welcome(view_manager), "dashboard": Dashboard(), "form": Form()}
