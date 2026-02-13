from __future__ import annotations

from datetime import timedelta
from typing import Final

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.parameters.argument_related_options import _make_argument_related_option
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleValue
from clive.__private.cli.common.parameters.styling import stylized_help
from clive.__private.cli.common.parsers import transaction_expiration_parser
from clive.__private.core.constants.date import (
    TRANSACTION_EXPIRATION_TIMEDELTA_MAX,
    TRANSACTION_EXPIRATION_TIMEDELTA_MIN,
)
from clive.__private.core.shorthand_timedelta import SHORTHAND_TIMEDELTA_EXAMPLE_SHORT, timedelta_to_shorthand_timedelta

transaction_expiration = CliveTyper(
    name="transaction-expiration", help="Manage the transaction expiration for the profile."
)

_EXPIRATION_HELP: Final[str] = (
    "Transaction expiration in shorthand format"
    f" ({SHORTHAND_TIMEDELTA_EXAMPLE_SHORT})."
    f" Min {timedelta_to_shorthand_timedelta(TRANSACTION_EXPIRATION_TIMEDELTA_MIN)},"
    f" max {timedelta_to_shorthand_timedelta(TRANSACTION_EXPIRATION_TIMEDELTA_MAX)}."
)

_expiration_argument = typer.Argument(
    None,
    metavar="TEXT",
    parser=transaction_expiration_parser,
    help=stylized_help(_EXPIRATION_HELP, required_as_arg_or_option=True),
)

_expiration_option = _make_argument_related_option(
    typer.Option(
        None,
        "--expiration",
        parser=transaction_expiration_parser,
    )
)


@transaction_expiration.command(name="set")
async def set_transaction_expiration(
    expiration: timedelta | None = _expiration_argument,
    expiration_option: timedelta | None = _expiration_option,
) -> None:
    """Set the transaction expiration for the profile. Check with `clive show profile`."""
    from clive.__private.cli.commands.configure.transaction_expiration import (  # noqa: PLC0415
        SetTransactionExpiration,
    )

    resolved = EnsureSingleValue[timedelta]("expiration").of(expiration, expiration_option)
    await SetTransactionExpiration(expiration=resolved).run()


@transaction_expiration.command(name="unset")
async def unset_transaction_expiration() -> None:
    """Reset the transaction expiration to the default value (30m)."""
    from clive.__private.cli.commands.configure.transaction_expiration import (  # noqa: PLC0415
        UnsetTransactionExpiration,
    )

    await UnsetTransactionExpiration().run()
