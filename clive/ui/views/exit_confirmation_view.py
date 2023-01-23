from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label

from clive.ui.view import View


class ExitConfirmationView(View):
    def _create_container(self) -> AnyContainer:
        from clive.app import clive  # TODO: Temporary solution

        clive.exit()
        return Label("Never reached")
