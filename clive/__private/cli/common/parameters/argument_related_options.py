from __future__ import annotations

from clive.__private.cli.common.parameters.options import account_name_option
from clive.__private.cli.common.parameters.utils import make_argument_related_option

account_name_argument_related_option = make_argument_related_option(account_name_option)
