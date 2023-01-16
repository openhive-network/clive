from clive.ui.dashboard_component import DashboardComponent
from clive.ui.view import View
from clive.ui.welcome_component import WelcomeComponent

views = {
    "welcome": View(WelcomeComponent()),
    "dashboard": View(DashboardComponent()),
}
