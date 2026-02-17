from __future__ import annotations

from datetime import datetime, timedelta  # noqa: TC003
from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import modified_param, options
from clive.__private.cli.common.parameters.styling import stylized_help
from clive.__private.cli.common.parsers import hbd_asset, hive_asset, hive_datetime, liquid_asset

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset

_who = modified_param(
    options.working_account_template,
    param_decls=("--who",),
    help=stylized_help("Account to act as.", is_working_account_default=True),
)

ESCROW_HELP = """\
Manage escrow transactions.

WORKFLOW:
  1. Sender creates escrow with receiver, agent, deadlines, and fee
  2. BOTH agent AND receiver must approve before ratification deadline
  3. If either rejects OR ratification deadline passes without both approvals,
     all funds (including the agent fee) return to the sender
  4. After both approve, escrow is active until all funds are released

RELEASE RULES:
  Before expiration (non-disputed):
    - Sender can only release to receiver
    - Receiver can only release to sender
  After expiration (non-disputed):
    - Sender and receiver can release to either party
  After dispute:
    - Only the agent can release funds (to either party)
  Partial releases are allowed - escrow remains active until fully drained.

AGENT FEE:
  - Fee is deducted from sender at escrow creation but held in escrow
  - Agent receives the fee only when BOTH agent and receiver approve
  - If escrow is rejected or expires before both approvals, fee returns to sender

DISPUTE:
  - Either sender or receiver can raise a dispute (after both approved)
  - Once disputed, only the agent can release funds
  - Agent decides who receives how much based on the situation
  - Without a dispute, the agent has no role in releasing funds

Your role is automatically detected based on your working account,
or the account specified with --who.
Use `clive show escrow` to view existing escrows.
"""

_who = modified_param(
    options.working_account_template,
    param_decls=("--who",),
    help=stylized_help("Account to act as.", is_working_account_default=True),
)

escrow = CliveTyper(name="escrow", help=ESCROW_HELP)


@escrow.command(name="transfer")
async def process_escrow_transfer(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to: str = typer.Option(..., "--to", help="The account to receive the escrowed funds."),
    agent: str = typer.Option(..., "--agent", help="The escrow agent account (mediator)."),
    escrow_id: int | None = typer.Option(
        None,
        "--escrow-id",
        help="Unique identifier for this escrow. If not given, will be automatically calculated.",
    ),
    hbd_amount: str = typer.Option(
        "0 HBD",
        "--hbd-amount",
        parser=hbd_asset,
        help="Amount of HBD to escrow (e.g., 100.000 HBD). "
        "At least one of --hbd-amount or --hive-amount must be non-zero.",
    ),
    hive_amount: str = typer.Option(
        "0 HIVE",
        "--hive-amount",
        parser=hive_asset,
        help="Amount of HIVE to escrow (e.g., 100.000 HIVE). "
        "At least one of --hbd-amount or --hive-amount must be non-zero.",
    ),
    fee: str = typer.Option(
        ...,
        "--fee",
        parser=liquid_asset,
        help="Fee paid to the agent (HBD or HIVE, e.g., 1.000 HBD).",
    ),
    ratification_deadline: str = typer.Option(  # actually datetime | timedelta, but Typer doesn't support Union types
        ...,
        "--ratification-deadline",
        parser=hive_datetime,
        help=(
            "Deadline by which BOTH agent AND receiver must approve. "
            "If not approved by this time, escrow is automatically cancelled. "
            "Formats: absolute (2024-12-31, 2024-12-31T14:30:00) or relative (+7d, +1w 2d). Time is UTC. "
            "Relative times are calculated from blockchain time."
        ),
    ),
    escrow_expiration: str = typer.Option(  # actually datetime | timedelta, but Typer doesn't support Union types
        ...,
        "--escrow-expiration",
        parser=hive_datetime,
        help=(
            "When escrow expires. Before expiration, release is limited (sender→receiver, receiver→sender only). "
            "After expiration, either party can release to anyone. Must be after ratification deadline. "
            "Formats: absolute (2024-12-31, 2024-12-31T14:30:00) or relative (+14d, +2w). Time is UTC. "
            "Relative times are calculated from blockchain time."
        ),
    ),
    json_meta: str = typer.Option(
        "",
        "--json-meta",
        help="JSON metadata for the escrow.",
    ),
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Create a new escrow transaction between accounts.

    See `clive process escrow --help` for full escrow workflow documentation.
    """
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowTransfer  # noqa: PLC0415

    await ProcessEscrowTransfer(
        from_account=from_account,
        to=to,
        agent=agent,
        escrow_id=escrow_id,
        hbd_amount=cast("Asset.Hbd", hbd_amount),
        hive_amount=cast("Asset.Hive", hive_amount),
        fee=cast("Asset.LiquidT", fee),
        ratification_deadline=cast("datetime | timedelta", ratification_deadline),
        escrow_expiration=cast("datetime | timedelta", escrow_expiration),
        json_meta=json_meta,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="approve")
async def process_escrow_approve(  # noqa: PLR0913
    escrow_owner: str = options.escrow_owner,
    escrow_id: int = typer.Option(
        ..., "--escrow-id", help="ID of the escrow to approve. Use `clive show escrow` to list escrow IDs."
    ),
    who: str = _who,
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Approve an escrow transaction.

    Only receiver or agent can approve. Sender cannot approve their own escrow.

    Your role (receiver or agent) is automatically detected based on your working account,
    or the account specified with --who.

    See `clive process escrow --help` for full escrow workflow documentation.
    """
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowApprove  # noqa: PLC0415

    await ProcessEscrowApprove(
        escrow_owner=escrow_owner,
        escrow_id=escrow_id,
        approve=True,
        who_override=who,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="reject")
async def process_escrow_reject(  # noqa: PLR0913
    escrow_owner: str = options.escrow_owner,
    escrow_id: int = typer.Option(
        ..., "--escrow-id", help="ID of the escrow to reject. Use `clive show escrow` to list escrow IDs."
    ),
    who: str = _who,
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Reject an escrow transaction.

    Only receiver or agent can reject. Sender cannot reject their own escrow.

    Rejecting returns all escrowed funds to the sender immediately.

    Your role (receiver or agent) is automatically detected based on your working account,
    or the account specified with --who.

    See `clive process escrow --help` for full escrow workflow documentation.
    """
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowApprove  # noqa: PLC0415

    await ProcessEscrowApprove(
        escrow_owner=escrow_owner,
        escrow_id=escrow_id,
        approve=False,
        who_override=who,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="dispute")
async def process_escrow_dispute(  # noqa: PLR0913
    escrow_owner: str = options.escrow_owner,
    escrow_id: int = typer.Option(
        ..., "--escrow-id", help="ID of the escrow to dispute. Use `clive show escrow` to list escrow IDs."
    ),
    who: str = _who,
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Raise a dispute on an escrow transaction.

    Only sender or receiver can raise a dispute. Agent cannot dispute.

    Once disputed, only the agent can release funds. Use this when you and the other
    party cannot agree on the release terms.

    Your role (sender or receiver) is automatically detected based on your working account,
    or the account specified with --who.

    See `clive process escrow --help` for full escrow workflow documentation.
    """
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowDispute  # noqa: PLC0415

    await ProcessEscrowDispute(
        escrow_owner=escrow_owner,
        escrow_id=escrow_id,
        who_override=who,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="release")
async def process_escrow_release(  # noqa: PLR0913
    escrow_owner: str = options.escrow_owner,
    escrow_id: int = typer.Option(
        ..., "--escrow-id", help="ID of the escrow to release funds from. Use `clive show escrow` to list escrow IDs."
    ),
    who: str = _who,
    receiver: str | None = typer.Option(
        None,
        "--receiver",
        help="Who receives the funds. Auto-filled for sender/receiver roles. Required for agent.",
    ),
    hbd_amount: str = typer.Option(
        "0 HBD",
        "--hbd-amount",
        parser=hbd_asset,
        help="Amount of HBD to release (e.g., 100.000 HBD).",
    ),
    hive_amount: str = typer.Option(
        "0 HIVE",
        "--hive-amount",
        parser=hive_asset,
        help="Amount of HIVE to release (e.g., 100.000 HIVE).",
    ),
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Release funds from an escrow.

    Release rules depend on escrow state:
      - Non-disputed, before expiration: sender→receiver or receiver→sender only
      - Non-disputed, after expiration: either party can release to anyone
      - Disputed: only agent can release

    Your role (sender, receiver, or agent) is automatically detected based on your working account,
    or the account specified with --who.

    Receiver auto-fill:
      - Sender releases to receiver (to account)
      - Receiver releases to sender (from account)
      - Agent must specify --receiver explicitly

    See `clive process escrow --help` for full escrow workflow documentation.
    """
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowRelease  # noqa: PLC0415

    await ProcessEscrowRelease(
        escrow_owner=escrow_owner,
        escrow_id=escrow_id,
        who_override=who,
        receiver=receiver,
        hbd_amount=cast("Asset.Hbd", hbd_amount),
        hive_amount=cast("Asset.Hive", hive_amount),
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()
