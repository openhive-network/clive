from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parsers import account_name

SOCIAL_HELP = """\
Manage social relationships on the Hive blockchain.

Social operations allow you to follow, unfollow, mute, or unmute accounts.
These operations use posting authority.
"""

social = CliveTyper(name="social", help=SOCIAL_HELP)


@social.command(name="follow")
async def process_social_follow(  # noqa: PLR0913
    account_name: str = options.account_name,
    user: str = typer.Option(..., "--user", parser=account_name, help="The account to follow."),
    sign_with: list[str] = options.sign_with_posting,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Follow an account."""
    from clive.__private.cli.commands.process.process_social import ProcessFollow  # noqa: PLC0415

    await ProcessFollow(
        follower=account_name,
        following=user,
        action="follow",
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@social.command(name="unfollow")
async def process_social_unfollow(  # noqa: PLR0913
    account_name: str = options.account_name,
    user: str = typer.Option(..., "--user", parser=account_name, help="The account to unfollow."),
    sign_with: list[str] = options.sign_with_posting,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Unfollow an account."""
    from clive.__private.cli.commands.process.process_social import ProcessFollow  # noqa: PLC0415

    await ProcessFollow(
        follower=account_name,
        following=user,
        action="unfollow",
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@social.command(name="mute")
async def process_social_mute(  # noqa: PLR0913
    account_name: str = options.account_name,
    user: str = typer.Option(..., "--user", parser=account_name, help="The account to mute."),
    sign_with: list[str] = options.sign_with_posting,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Mute an account."""
    from clive.__private.cli.commands.process.process_social import ProcessFollow  # noqa: PLC0415

    await ProcessFollow(
        follower=account_name,
        following=user,
        action="mute",
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@social.command(name="unmute")
async def process_social_unmute(  # noqa: PLR0913
    account_name: str = options.account_name,
    user: str = typer.Option(..., "--user", parser=account_name, help="The account to unmute."),
    sign_with: list[str] = options.sign_with_posting,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Unmute an account."""
    from clive.__private.cli.commands.process.process_social import ProcessFollow  # noqa: PLC0415

    await ProcessFollow(
        follower=account_name,
        following=user,
        action="unmute",
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()
