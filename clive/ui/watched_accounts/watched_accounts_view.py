from prompt_toolkit.widgets import Label

from clive.ui.view import View


class WatchedAccountsView(View):
    def _create_container(self) -> Label:
        return Label(text=self.__class__.__name__)
