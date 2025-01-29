from dataclasses import dataclass

from clive.__private.cli.common.parameters.groups.parameter_group import ParameterGroup


@dataclass(kw_only=True)
class WorldOptionsGroup(ParameterGroup): ...
