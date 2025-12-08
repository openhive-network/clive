from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager

EnvContextFactory = Callable[[str | None], AbstractContextManager[None]]
GenericEnvContextFactory = Callable[[str], EnvContextFactory]
