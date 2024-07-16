from __future__ import annotations

from typing import TYPE_CHECKING, Any

import test_tools as tt

from clive.__private.cli.commands.show.show_transfer_schedule import DEFAULT_UPCOMING_FUTURE_SCHEDULED_TRANSFERS_AMOUNT

TABLE_ROW_SPLIT_SYMBOL_START = "│ "
TABLE_ROW_SPLIT_SYMBOL_END = " │"
TABLE_ROW_SPLIT_SYMBOL_MIDDLE = " │ "

TABLE_START = "──"
TABLE_END = "──"

TABLE_HEADER_SYMBOL_START = "┃ "
TABLE_HEADER_SYMBOL_END = " ┃"
TABLE_HEADER_SYMBOL_MIDDLE = " ┃ "


TableRowType = dict[str, Any]
TableDataType = list[TableRowType]

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


def strip_garbage(arg: str) -> str:
    """
    Strip table formatting symbols from the given string.

    Args:
    ----
        arg (str): The string to strip formatting symbols from.

    Returns:
    -------
        str: The stripped string.
    """
    if TABLE_HEADER_SYMBOL_START in arg:
        arg = arg.lstrip(TABLE_HEADER_SYMBOL_START)
    if TABLE_HEADER_SYMBOL_END in arg:
        arg = arg.rstrip(TABLE_HEADER_SYMBOL_END)
    if TABLE_ROW_SPLIT_SYMBOL_START in arg:
        arg = arg.lstrip(TABLE_ROW_SPLIT_SYMBOL_START)
    if TABLE_ROW_SPLIT_SYMBOL_END in arg:
        arg = arg.rstrip(TABLE_ROW_SPLIT_SYMBOL_END)
    return arg.strip()


def get_table_data_from_output(output: str, table_name: str) -> TableDataType:
    """
    Extract table data from the given output string based on the specified table name.

    Args:
    ----
        output (str): The output string containing the table data.
        table_name (str): The name of the table to search for in the output.

    Returns:
    -------
        A list of dictionaries representing the table data
    """
    lines = output.split("\n")
    table_found = False
    header_arguments: list[str] = []
    values: list[list[str]] = []

    for line in lines:
        if table_name in line:
            table_found = True
            continue
        if table_found:
            if line.startswith(TABLE_HEADER_SYMBOL_START):
                header_arguments = [strip_garbage(arg) for arg in line.split(TABLE_HEADER_SYMBOL_MIDDLE)]
            elif line.startswith(TABLE_ROW_SPLIT_SYMBOL_START):
                values.append([strip_garbage(val) for val in line.split(TABLE_ROW_SPLIT_SYMBOL_MIDDLE)])
            elif TABLE_END in line:
                break

    if not table_found:
        raise ValueError(f"Table `{table_name}` was not found.")

    if header_arguments and values:
        return [dict(zip(header_arguments, v)) for v in values]

    raise ValueError(f"Table `{table_name}` structure is incomplete or improperly formatted.")


def get_data_from_balances_table_for(output: str, account_name: str) -> TableDataType:
    """Extract table data from result.output of `clive show balances` command."""
    return get_table_data_from_output(output, f"Balances of `{account_name}` account")


def get_data_from_scheduled_transfer_definition_table_for(output: str, account_name: str) -> TableDataType:
    """Extract table `Transfer schedule definitions...` data from result.output of `clive show transfer-schedule` command."""  # noqa: E501
    return get_table_data_from_output(output, f"Transfer schedule definitions for `{account_name}` account")


def get_data_from_scheduled_transfer_upcoming_table_for(output: str, account_name: str) -> TableDataType:
    """Extract table `Next {DEFAULT}...` data from result.output of `clive show transfer-schedule` command."""
    return get_table_data_from_output(
        output,
        (
            f"Next {DEFAULT_UPCOMING_FUTURE_SCHEDULED_TRANSFERS_AMOUNT} "
            f"upcoming recurrent transfers for `{account_name}` account"
        ),
    )


def get_account_balance(cli_tester: CLITester, account_name: str) -> TableRowType:
    """
    Fetch balances from node for given account, and format it into simple dict.

    Returns
    -------
        dict :
            {'HBD Liquid': '100000.000',
             'HBD Savings': '190.000',
             'HBD Unclaimed': '0.000',
             'HIVE Liquid': '99999.000',
             'HIVE Savings': '100.000',
             'HIVE Unclaimed': '0.000'}

    """
    result = cli_tester.show_balances(account_name=account_name)
    balance_table_data = get_data_from_balances_table_for(result.stdout, account_name)
    balances: TableRowType = {}
    for balance in balance_table_data:
        balances[balance["Type"]] = balance["Amount"]
    return balances


def get_account_liquid_balance(
    cli_tester: CLITester, account_name: str, *, hive: bool
) -> tt.Asset.HiveT | tt.Asset.HbdT:
    account_balances = get_account_balance(cli_tester, account_name)
    if hive:
        return tt.Asset.Hive(account_balances["HIVE Liquid"])
    return tt.Asset.Hbd(account_balances["HBD Liquid"])
