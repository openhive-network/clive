from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.table import Table


def add_pagination_info_to_table_if_needed(table: Table, page_no: int, page_size: int, all_entries: int) -> None:
    """
    Add information about current displayed page of table.

    Args:
        table: The table to which the pagination info will be added.
        page_no: The current page number (0-indexed).
        page_size: The number of entries per page.
        all_entries: The total number of entries available.
    """
    assert page_no >= 0, "Page number must be greater or equal to 0."
    assert page_size > 0, "Page size must be greater than 0."
    assert table.caption is None, "The table's caption should be None before setting a new one to avoid overwriting."

    if page_no == 0 and page_size >= all_entries:
        return

    last_page_no = math.ceil(all_entries / page_size) - 1  # -1 as pages are 0-indexed

    if page_no == 0:
        page_info = "There are more on the next page(s)."
    elif page_no >= last_page_no:
        page_info = "There are more on the previous page(s)."
    else:
        page_info = "There are more on the next/previous page(s)."

    # Setting caption
    table.caption = page_info
    table.caption_style = "default"  # Set text background color to default - it will be the same as terminal
