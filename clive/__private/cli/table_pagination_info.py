from rich.align import Align
from rich.columns import Columns
from rich.console import Group
from rich.table import Table


def add_pagination_info_if_needed(table: Table, page_no: int, page_size: int, all_entries: int) -> Table | Columns:
    """Add information about current displayed page of table."""
    max_pages = all_entries // page_size

    if all_entries % page_size == 0:
        """
        In order to avoid adding additional page with empty content.

        For example:
            all_entries = 20:
            page_size = 5

        We would get 4, but we have content on 0-3 pages.
        """
        max_pages -= 1

    if max_pages > page_no:
        centered_text = Align(f"There are more on next page ({page_no}/{max_pages})", align="center")
        group = Group(table, centered_text)
        return Columns([group], align="center")
    return table
