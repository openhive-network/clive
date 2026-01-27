from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parsers import hbd_asset, hive_asset, hive_datetime, liquid_asset

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset

ESCROW_HELP = """\
Manage escrow transactions.

Escrow flow:
  1. Sender creates escrow (transfer) with receiver, agent, and deadlines
  2. Agent and receiver must approve before ratification deadline
  3. After approval, sender can release funds to receiver
  4. If dispute arises, either party can raise it
  5. After dispute, agent decides fund distribution

Commands by stage:
  Create:   transfer
  Approve:  approve-by-agent, approve-by-receiver
  Reject:   reject-by-agent, reject-by-receiver
  Dispute:  dispute-by-sender, dispute-by-receiver
  Release:  release-by-sender, release-by-receiver, release-by-agent
"""

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
        help="Amount of HBD to escrow (e.g., 100.000 HBD). At least one of --hbd-amount or --hive-amount must be non-zero.",
    ),
    hive_amount: str = typer.Option(
        "0 HIVE",
        "--hive-amount",
        parser=hive_asset,
        help="Amount of HIVE to escrow (e.g., 100.000 HIVE). At least one of --hbd-amount or --hive-amount must be non-zero.",
    ),
    fee: str = typer.Option(
        ...,
        "--fee",
        parser=liquid_asset,
        help="Fee paid to the agent (HBD or HIVE, e.g., 1.000 HBD).",
    ),
    ratification_deadline: datetime = typer.Option(
        ...,
        "--ratification-deadline",
        parser=hive_datetime,
        help="Deadline for agent/receiver approval (e.g., 2024-12-31 or 2024-12-31T14:30:00).",
    ),
    escrow_expiration: datetime = typer.Option(
        ...,
        "--escrow-expiration",
        parser=hive_datetime,
        help="When escrow expires and can be released (e.g., 2025-01-15 or 2025-01-15T12:00:00).",
    ),
    json_meta: str = typer.Option(
        "",
        "--json-meta",
        help="JSON metadata for the escrow.",
    ),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Create a new escrow transaction between accounts."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowTransfer  # noqa: PLC0415

    await ProcessEscrowTransfer(
        from_account=from_account,
        to=to,
        agent=agent,
        escrow_id=escrow_id,
        hbd_amount=cast("Asset.Hbd", hbd_amount),
        hive_amount=cast("Asset.Hive", hive_amount),
        fee=cast("Asset.LiquidT", fee),
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        json_meta=json_meta,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="approve-by-agent")
async def process_escrow_approve_by_agent(  # noqa: PLR0913
    from_account: str = options.from_account_name_required,
    to: str = typer.Option(..., "--to", help="The escrow receiver account."),
    agent: str = options.agent_account_name,
    escrow_id: int = typer.Option(..., "--escrow-id", help="ID of the escrow to approve."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Approve an escrow as the agent."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowApprove  # noqa: PLC0415

    await ProcessEscrowApprove(
        from_account=from_account,
        to=to,
        agent=agent,
        who=agent,
        escrow_id=escrow_id,
        approve=True,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="approve-by-receiver")
async def process_escrow_approve_by_receiver(  # noqa: PLR0913
    from_account: str = options.from_account_name_required,
    to: str = options.to_account_name,
    agent: str = typer.Option(..., "--agent", help="The escrow agent account."),
    escrow_id: int = typer.Option(..., "--escrow-id", help="ID of the escrow to approve."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Approve an escrow as the receiver."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowApprove  # noqa: PLC0415

    await ProcessEscrowApprove(
        from_account=from_account,
        to=to,
        agent=agent,
        who=to,
        escrow_id=escrow_id,
        approve=True,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="reject-by-agent")
async def process_escrow_reject_by_agent(  # noqa: PLR0913
    from_account: str = options.from_account_name_required,
    to: str = typer.Option(..., "--to", help="The escrow receiver account."),
    agent: str = options.agent_account_name,
    escrow_id: int = typer.Option(..., "--escrow-id", help="ID of the escrow to reject."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Reject an escrow as the agent."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowApprove  # noqa: PLC0415

    await ProcessEscrowApprove(
        from_account=from_account,
        to=to,
        agent=agent,
        who=agent,
        escrow_id=escrow_id,
        approve=False,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="reject-by-receiver")
async def process_escrow_reject_by_receiver(  # noqa: PLR0913
    from_account: str = options.from_account_name_required,
    to: str = options.to_account_name,
    agent: str = typer.Option(..., "--agent", help="The escrow agent account."),
    escrow_id: int = typer.Option(..., "--escrow-id", help="ID of the escrow to reject."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Reject an escrow as the receiver."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowApprove  # noqa: PLC0415

    await ProcessEscrowApprove(
        from_account=from_account,
        to=to,
        agent=agent,
        who=to,
        escrow_id=escrow_id,
        approve=False,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="dispute-by-sender")
async def process_escrow_dispute_by_sender(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to: str = typer.Option(..., "--to", help="The escrow receiver account."),
    agent: str = typer.Option(..., "--agent", help="The escrow agent account."),
    escrow_id: int = typer.Option(..., "--escrow-id", help="ID of the escrow to dispute."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Raise a dispute on an escrow as the sender."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowDispute  # noqa: PLC0415

    await ProcessEscrowDispute(
        from_account=from_account,
        to=to,
        agent=agent,
        who=from_account,
        escrow_id=escrow_id,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="dispute-by-receiver")
async def process_escrow_dispute_by_receiver(  # noqa: PLR0913
    from_account: str = options.from_account_name_required,
    to: str = options.to_account_name,
    agent: str = typer.Option(..., "--agent", help="The escrow agent account."),
    escrow_id: int = typer.Option(..., "--escrow-id", help="ID of the escrow to dispute."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Raise a dispute on an escrow as the receiver."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowDispute  # noqa: PLC0415

    await ProcessEscrowDispute(
        from_account=from_account,
        to=to,
        agent=agent,
        who=to,
        escrow_id=escrow_id,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="release-by-sender")
async def process_escrow_release_by_sender(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to: str = typer.Option(..., "--to", help="The escrow receiver account."),
    agent: str = typer.Option(..., "--agent", help="The escrow agent account."),
    receiver: str = typer.Option(..., "--receiver", help="Who receives the funds (account name)."),
    escrow_id: int = typer.Option(..., "--escrow-id", help="ID of the escrow to release."),
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
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Release funds from an escrow as the sender."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowRelease  # noqa: PLC0415

    await ProcessEscrowRelease(
        from_account=from_account,
        to=to,
        agent=agent,
        who=from_account,
        receiver=receiver,
        escrow_id=escrow_id,
        hbd_amount=cast("Asset.Hbd", hbd_amount),
        hive_amount=cast("Asset.Hive", hive_amount),
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="release-by-receiver")
async def process_escrow_release_by_receiver(  # noqa: PLR0913
    from_account: str = options.from_account_name_required,
    to: str = options.to_account_name,
    agent: str = typer.Option(..., "--agent", help="The escrow agent account."),
    receiver: str = typer.Option(..., "--receiver", help="Who receives the funds (account name)."),
    escrow_id: int = typer.Option(..., "--escrow-id", help="ID of the escrow to release."),
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
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Release funds from an escrow as the receiver."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowRelease  # noqa: PLC0415

    await ProcessEscrowRelease(
        from_account=from_account,
        to=to,
        agent=agent,
        who=to,
        receiver=receiver,
        escrow_id=escrow_id,
        hbd_amount=cast("Asset.Hbd", hbd_amount),
        hive_amount=cast("Asset.Hive", hive_amount),
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@escrow.command(name="release-by-agent")
async def process_escrow_release_by_agent(  # noqa: PLR0913
    from_account: str = options.from_account_name_required,
    to: str = typer.Option(..., "--to", help="The escrow receiver account."),
    agent: str = options.agent_account_name,
    receiver: str = typer.Option(..., "--receiver", help="Who receives the funds (account name)."),
    escrow_id: int = typer.Option(..., "--escrow-id", help="ID of the escrow to release."),
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
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Release funds from an escrow as the agent (after dispute)."""
    from clive.__private.cli.commands.process.process_escrow import ProcessEscrowRelease  # noqa: PLC0415

    await ProcessEscrowRelease(
        from_account=from_account,
        to=to,
        agent=agent,
        who=agent,
        receiver=receiver,
        escrow_id=escrow_id,
        hbd_amount=cast("Asset.Hbd", hbd_amount),
        hive_amount=cast("Asset.Hive", hive_amount),
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()
