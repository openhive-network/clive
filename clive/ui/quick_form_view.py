
from prompt_toolkit.layout import AnyContainer

from clive.ui.form_view import FormView, RequestedButtonsT
from clive.ui.view import View
from clive.ui.views.form import Form


class QuickFormView(FormView):
    def __init__(self, *, parent: Form, view: View, request_buttons: RequestedButtonsT):
        self.__view = view
        self.__requested_buttons = request_buttons
        super().__init__(parent)

    def requested_buttons(self) -> RequestedButtonsT:
        return self.__requested_buttons

    def _create_container(self) -> AnyContainer:
        return self.__view.container
