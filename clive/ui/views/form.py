from __future__ import annotations

from typing import List

from clive.ui.components.form_buttons import FormButtons
from clive.ui.form_view import FormView
from clive.ui.views.button_based import ButtonsBased


class Form(ButtonsBased[FormView, FormButtons]):
    def __init__(self, views: List[FormView]) -> None:
        assert len(views) > 0
        self.__views = views
        self.__view_index = 0
        super().__init__(self.__views[0], FormButtons.merge_buttons_and_actions(self, self.current_view))

    @property
    def current_view(self) -> FormView:
        return self.__views[self.__view_index]

    def next_view(self) -> None:
        if self._reached_last_view():
            return

        self.__view_index += 1
        self._update_main_panel()

    def previous_view(self) -> None:
        if self._reached_first_view():
            return

        self.__view_index -= 1
        self._update_main_panel()

    def _update_main_panel(self) -> None:
        self.current_view._rebuild()
        self.main_panel = self.current_view
        self.buttons = FormButtons.merge_buttons_and_actions(self, self.current_view)

    def cancel(self) -> None:
        raise NotImplementedError("Cancel not implemented yet!")

    def _reached_last_view(self) -> bool:
        return self.__view_index == len(self.__views) - 1

    def _reached_first_view(self) -> bool:
        return self.__view_index == 0
