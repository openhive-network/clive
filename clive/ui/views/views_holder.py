from __future__ import annotations

from typing import TYPE_CHECKING

from clive.ui.views.dashboard import Dashboard
from clive.ui.welcome_component import WelcomeComponent

if TYPE_CHECKING:
    from clive.ui.view import View

views: dict[str, View] = {
    "welcome": WelcomeComponent(),
    "dashboard": Dashboard(),
}
