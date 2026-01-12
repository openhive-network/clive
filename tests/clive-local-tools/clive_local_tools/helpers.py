from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
import test_tools as tt
from rich.panel import Panel
from typer import rich_utils

from clive.__private.cli.print_cli import print_cli
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


def get_formatted_error_message(error: ClickException, *, escape: bool = True) -> str:
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
        print_cli(panel, console=console)
    if escape:
        # Escape special characters for regex matching, use when in message are
        # special regex characters like `(`, `)` etc.
        # Set this to True, when using together with get_formatted_error_message and pytest.raise(match=)
        # because if there are special characters in the message, it will cause errors in regex matching.
        # If you want to see the message as is, set escape to False.
        return re.escape(capture.get())
    return capture.get()


def create_transaction_filepath(identifier: str = "") -> Path:
    directory = tt.context.get_current_directory()
    identifier_postfix = f"_{identifier}" if identifier else ""
    file_name = f"transaction{identifier_postfix}.json"
    return directory / file_name


def create_transaction_file(content: TransactionConvertibleType, identifier: str = "") -> Path:
    transaction_filepath = create_transaction_filepath(identifier)
    transaction = ensure_transaction(content)
    transaction_serialized = transaction.json(indent=4)
    transaction_filepath.write_text(transaction_serialized)
    return transaction_filepath


def get_operation_from_transaction[OperationT](
    node: tt.RawNode, transaction_id: str, operation_type: type[OperationT]
) -> OperationT:
    """
    Get an operation of a specific type from a transaction.

    Args:
        node: The node to query for the transaction.
        transaction_id: The ID of the transaction to look up.
        operation_type: The expected type of the operation.

    Returns:
        The operation of the specified type.

    Raises:
        AssertionError: If the transaction doesn't contain exactly one operation of the expected type.
    """
    node.wait_number_of_blocks(1)
    transaction = node.api.account_history.get_transaction(id_=transaction_id, include_reversible=True)

    assert len(transaction.operations) == 1, f"Expected 1 operation, got {len(transaction.operations)}"
    op = transaction.operations[0]
    assert isinstance(op.value, operation_type), f"Expected {operation_type.__name__}, got {type(op.value).__name__}"
    return op.value
