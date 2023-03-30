from __future__ import annotations

from clive.__private.core.world import World
from clive.version import VERSION as __VERSION

__version__ = __VERSION.serialize()

__all__ = [
    "__version__",
    "World",
]
