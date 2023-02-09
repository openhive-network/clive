from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from clive.ui.dashboard.dashboard import Dashboard
from clive.ui.views.login import Login
from clive.ui.views.registration import Registration
from clive.ui.views.welcome import Welcome

if TYPE_CHECKING:
    from clive.ui.view import View

views: dict[str, Callable[[], View]] = {
    "welcome": lambda: Welcome(),
    "login": lambda: Login(),
    "dashboard": lambda: Dashboard(),
    "registration": lambda: Registration(),
}
