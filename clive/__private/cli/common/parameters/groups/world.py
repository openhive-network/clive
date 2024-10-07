from dataclasses import dataclass
from typing import Optional

from clive.__private.cli.common.parameters import options
from clive.__private.cli.common.parameters.groups.parameter_group import ParameterGroup


@dataclass(kw_only=True)
class WorldOptionsGroup(ParameterGroup):
    beekeeper_remote: Optional[str] = options.beekeeper_remote
