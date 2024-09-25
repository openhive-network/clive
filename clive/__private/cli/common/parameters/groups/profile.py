from dataclasses import dataclass
from typing import Optional

from clive.__private.cli.common.parameters import argument_related_options, arguments, options
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleProfileNameValue
from clive.__private.cli.common.parameters.groups.parameter_group import ParameterGroup


@dataclass(kw_only=True)
class ProfileOptionsGroup(ParameterGroup):
    profile_name: str = options.profile_name


@dataclass(kw_only=True)
class ProfileNameArgumentAndOptionGroup(ParameterGroup):
    profile_name: Optional[str] = arguments.profile_name
    profile_name_option: Optional[str] = argument_related_options.profile_name

    def ensure_single_profile_name_value(self) -> str:
        return EnsureSingleProfileNameValue().of(self.profile_name, self.profile_name_option)
