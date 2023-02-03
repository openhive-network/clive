from __future__ import annotations

from abc import abstractmethod
from typing import List

from clive.exceptions import FormNotFinishedException
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

        self.__assert_is_view_valid(self.__view_index)

        self.__view_index += 1
        self.update_main_panel()

    def previous_view(self) -> None:
        if self._reached_first_view():
            return

        self.__assert_is_view_valid(self.__view_index)

        self.__view_index -= 1
        self.update_main_panel()

    def update_main_panel(self) -> None:
        self.current_view._rebuild()
        self.main_panel = self.current_view
        self.buttons = FormButtons.merge_buttons_and_actions(self, self.current_view)

    def __assert_is_view_valid(self, view_index: int) -> None:
        checkpoints = self.__views[view_index].is_valid()
        for checkpoint_description, check_passed in checkpoints.items():
            if not check_passed:
                raise FormNotFinishedException(**{checkpoint_description: check_passed})

    @abstractmethod
    def cancel(self) -> None:
        ...

    @abstractmethod
    def finish(self) -> None:
        ...

    def _finish(self) -> None:
        for i in range(len(self.__views)):
            self.__assert_is_view_valid(i)
        self.finish()

    def _reached_last_view(self) -> bool:
        return self.__view_index == len(self.__views) - 1

    def _reached_first_view(self) -> bool:
        return self.__view_index == 0
