from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rich.panel import Panel
from typer import rich_utils

from clive.__private.core.constants.terminal import TERMINAL_HEIGHT, TERMINAL_WIDTH
from clive.__private.core.ensure_transaction import TransactionConvertibleType, ensure_transaction
from clive.__private.models.schemas import TransactionId, validate_schema_field

if TYPE_CHECKING:
    from pathlib import Path

    from click import ClickException


def get_transaction_id_from_output(output: str) -> str:
    for line in output.split("\n"):
        transaction_id = line.partition('"transaction_id":')[2]
        if transaction_id:
            transaction_id_field = transaction_id.strip(' "')
            validate_schema_field(transaction_id_field, TransactionId)
            return transaction_id_field
    pytest.fail(f"Could not find transaction id in output {output}")


def get_formatted_error_message(error: ClickException) -> str:
    panel = Panel(
        rich_utils.highlighter(error.format_message()),
        border_style=rich_utils.STYLE_ERRORS_PANEL_BORDER,
        title=rich_utils.ERRORS_PANEL_TITLE,
        title_align=rich_utils.ALIGN_ERRORS_PANEL,
    )
    console = rich_utils._get_rich_console(stderr=True)
    console.width = TERMINAL_WIDTH
    console.height = TERMINAL_HEIGHT
    # Turn off colors, in order to prevent from adding ascii color markers.
    # It causes errors while running `pytest -s`
    console._color_system = None
    with console.capture() as capture:
        console.print(panel)
    return capture.get()


def create_transaction_file(path: Path, content: TransactionConvertibleType) -> Path:
    transaction_path = path / "trx.json"
    transaction = ensure_transaction(content)
    transaction_serialized = transaction.json()
    transaction_path.write_text(transaction_serialized)
    return transaction_path
