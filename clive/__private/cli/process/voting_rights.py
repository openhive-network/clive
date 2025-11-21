from __future__ import annotations

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

voting_rights = CliveTyper(
    name="voting-rights",
    help=(
        "After 30 days from starting the decline, cancellation is no longer possible"
        ", and the operation cannot be undone."
    ),
)


@voting_rights.command(name="decline")
async def process_voting_rights_decline(
    account_name: str = options.account_name,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Will take effect after 30 days. Until then it can be cancelled, but later is permanent. Requires owner authority.

    Using the decline_voting_rights_operation, a user may choose to decline their voting rights \
- for content, witnesses, and proposals - and cannot set a proxy. \
Use command 'clive show pending decline-voting-rights' to display 'decline_voting_rights_operation' in progress.
    """
    from clive.__private.cli.commands.process.process_voting_rights import (  # noqa: PLC0415
        ProcessVotingRightsDecline,
    )

    await ProcessVotingRightsDecline(
        account_name=account_name,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@voting_rights.command(name="cancel-decline")
async def process_voting_rights_cancel_decline(
    account_name: str = options.account_name,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    During the 30-day delay before the change takes effect, you may cancel declining. Requires owner authority.

    After this period, the decline becomes permanent and cannot be undone.
    """
    from clive.__private.cli.commands.process.process_voting_rights import (  # noqa: PLC0415
        ProcessVotingRightsCancelDecline,
    )

    await ProcessVotingRightsCancelDecline(
        account_name=account_name,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()
