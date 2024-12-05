from dataclasses import dataclass, field
from typing import Optional

from clive.__private.cli.common.parameters import options
from clive.__private.cli.common.parameters.groups.parameter_group import ParameterGroup


@dataclass(kw_only=True)
class WorldOptionsGroup(ParameterGroup):
    profile_name: str = options.profile_name
    beekeeper_remote: Optional[str] = options.beekeeper_remote
    use_beekeeper: bool = field(default=True, metadata={"ignore": True})
