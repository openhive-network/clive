from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

import pytest
import test_tools as tt
from rich.panel import Panel
from typer import rich_utils

from clive.__private.cli.print_cli import print_cli
from clive.__private.core.constants.terminal import TERMINAL_HEIGHT, TERMINAL_WIDTH
from clive.__private.core.ensure_transaction import TransactionConvertibleType, ensure_transaction
from clive.__private.models.schemas import GetTransaction, TransactionId, validate_schema_field
from schemas.convert import to_builtins

if TYPE_CHECKING:
    from pathlib import Path

    from click import ClickException
    from hiveio_api.common import NaiAsset

    from clive.__private.models.schemas import AssetHbd, AssetHive, AssetVests, PreconfiguredBaseModel


def get_signatures_count_from_output(output: str) -> int:
    start = output.index("{")
    tx, _ = json.JSONDecoder().raw_decode(output, start)
    return len(tx.get("signatures", []))


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
    transaction = convert_api_response(
        node.api.account_history.get_transaction(id_=transaction_id, include_reversible=True), GetTransaction
    )

    assert len(transaction.operations) == 1, f"Expected 1 operation, got {len(transaction.operations)}"
    op = transaction.operations[0]
    assert isinstance(op.value, operation_type), f"Expected {operation_type.__name__}, got {type(op.value).__name__}"
    return op.value


def convert_api_response[ModelT: PreconfiguredBaseModel](response: object, model: type[ModelT]) -> ModelT:
    """
    Convert a response of the test-tools node API into the corresponding schemas model.

    Test-tools returns hiveio-api models, in which e.g. operations are plain dictionaries and timestamps are strings.
    Converting the response allows comparing it with the schemas models that clive uses.

    Args:
        response: The response returned by the test-tools node API.
        model: The schemas model to convert the response into.

    Returns:
        The response converted into the given model.
    """
    return model.parse_builtins(to_builtins(response))


def convert_nai_asset[AssetT: AssetHive | AssetHbd | AssetVests](asset: NaiAsset, asset_type: type[AssetT]) -> AssetT:
    """
    Convert an asset returned by the test-tools node API (hiveio-api NaiAsset) into the schemas asset.

    Args:
        asset: The asset returned by the test-tools node API.
        asset_type: The expected type of the asset.

    Returns:
        The asset converted into the expected type.

    Raises:
        AssertionError: If the asset is not of the expected type.
    """
    converted = tt.Asset.from_nai(to_builtins(asset))
    assert isinstance(converted, asset_type), f"Expected {asset_type.__name__}, got {type(converted).__name__}"
    return converted
