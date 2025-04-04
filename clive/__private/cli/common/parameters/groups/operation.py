from dataclasses import dataclass
from typing import Optional

from clive.__private.cli.common.parameters import options
from clive.__private.cli.common.parameters.groups.parameter_group import ParameterGroup


@dataclass(kw_only=True)
class OperationOptionsGroup(ParameterGroup):
    sign: Optional[str] = options.sign
    broadcast: bool = options.broadcast
    save_file: Optional[str] = options.save_file
