from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.contextual import Context

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.__private.core.profile import Profile


@dataclass
class CreateProfileContext(Context):
    profile: Profile
    node: Node
