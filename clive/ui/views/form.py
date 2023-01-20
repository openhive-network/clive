from __future__ import annotations
from typing import List

from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label

from clive.ui.components.form_buttons import FormButtons
from clive.ui.form_view import FormView
from clive.ui.views.button_based import ButtonsBased


class Form(ButtonsBased):
    def __init__(self, views: List[FormView]) -> None:
        self.__views = views
        self.__view_index = 0
        super().__init__(self.__views[0], FormButtons(self))

    def next_view(self) -> None:
        if self.__reached_last_view():
            return

        self.__view_index += 1
        self.main_pane = self.__views[self.__view_index]

    def previous_view(self) -> None:
        if self.__reached_first_view():
            return

        self.__view_index -= 1
        self.main_pane = self.__views[self.__view_index]

    def cancel(self) -> None:
        raise NotImplementedError("Cancel not implemented yet!")

    def __reached_last_view(self) -> bool:
        return self.__view_index == len(self.__views) - 1

    def __reached_first_view(self) -> bool:
        return self.__view_index == 0


class First(FormView):
    def _create_container(self) -> AnyContainer:
        return Label("First view")


class Second(FormView):
    def _create_container(self) -> AnyContainer:
        return Label("Second view")


class Third(FormView):
    def _create_container(self) -> AnyContainer:
        return Label("Third view")
