from __future__ import annotations

from typing import TYPE_CHECKING

from clive.ui.views.dashboard import Dashboard
from clive.ui.views.welcome import Welcome

if TYPE_CHECKING:
    from clive.ui.view import View

views: dict[str, View] = {
    "welcome": Welcome(),
    "dashboard": Dashboard(),
}
