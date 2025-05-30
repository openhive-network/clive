from __future__ import annotations

from pydantic import Field

from clive.__private.core.constants.env import BINDINGS_FILE
from clive.__private.models.base import CliveBaseModel


class Global(CliveBaseModel):
    help: tuple[str, str] = ("f1", "?")
    switch_mode_into_locked: str = "ctrl+l"
    go_to_dashboard: str = "ctrl+d"
    go_to_transaction_summary: str = "ctrl+t"
    go_to_switch_node_binding: str = "ctrl+n"
    go_to_settings: str = "ctrl+s"
    clear_notifications: str = "ctrl+x"
    go_to_load_transaction_from_file: str = "ctrl+o"
    app_quit: str = "ctrl+q"
    quit_immediately: str = "ctrl+c"
    screenshot: str = "ctrl+p"


class Bindings(CliveBaseModel):
    next_screen: str = "ctrl+n"
    previous_screen: str = "ctrl+p"
    finalize_transaction: str = "f"
    save_transaction_to_file: str = "s"
    add_operation_to_cart: str = "a"
    broadcast_transaction: str = "b"
    load_transaction_from_file: str = "o"
    refresh_transaction_metadata: str = "u"

    global_: Global = Field(default_factory=Global, alias="global")


bindings = Bindings.parse_file(BINDINGS_FILE)
