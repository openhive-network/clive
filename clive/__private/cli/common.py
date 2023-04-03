from __future__ import annotations

import typer

Broadcast = typer.Option(..., help="Broadcast the transaction.", show_default=False)
Sign = typer.Option(..., help="Key alias to sign the transaction with.")
Profile = typer.Option(..., help="The profile to use.")
Password = typer.Option(..., help="The password to use.")
SaveFile = typer.Option(None, help="The file to save the transaction to.")
