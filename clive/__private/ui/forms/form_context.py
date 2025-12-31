from __future__ import annotations

from typing import TypeVar

from clive.__private.core.contextual import Context


class NoContext(Context):
    """A class that signals that there is no context."""


FormContextT = TypeVar("FormContextT", bound=Context, default=NoContext)
