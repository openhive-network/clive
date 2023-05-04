from __future__ import annotations

from typing import TYPE_CHECKING

from textual.dom import DOMNode

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


class ManualReactive(DOMNode):
    def update_reactive(self, attribute_name: str, update_function: Callable[[Any], None] | None = None) -> None:
        """
        Reactive attributes of Textual are unable to detect changes to their own attributes
        (if we are dealing with a non-primitive type like a custom class).
        In order to notify watchers of a reactive attribute, it would have to be re-instantiated with the modified
        attributes. (See https://github.com/Textualize/textual/discussions/1099#discussioncomment-4047932)
        This is where this method comes in handy.
        """
        try:
            attribute = getattr(self, attribute_name)
        except AttributeError as error:
            raise AttributeError(f"{error}. Available ones are: {list(self._reactives)}") from error

        descriptor = self.__class__.__dict__[attribute_name]

        if update_function is not None:
            update_function(attribute)  # modify attributes of the reactive attribute

        # now we trigger the descriptor.__set__ method like the `self.attribute_name = value` would do
        if not descriptor._always_update:
            # that means, watchers won't be notified unless __ne__ returns False, we could bypass with `always_update`
            descriptor._always_update = True
            setattr(self, attribute_name, attribute)
            descriptor._always_update = False
        else:
            # we just need to trigger descriptor.__set__
            setattr(self, attribute_name, attribute)
