from __future__ import annotations

from dataclasses import dataclass, field

from clive.__private.ui.bindings.clive_binding import CliveBinding
from clive.__private.ui.bindings.clive_binding_section import CliveBindingSection


@dataclass
class App(CliveBindingSection):
    clear_notifications: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="clear_notifications", key="ctrl+x")
    )
    dashboard: CliveBinding = field(default_factory=lambda: CliveBinding(id="dashboard", key="ctrl+d"))
    load_transaction_from_file: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="load_transaction_from_file", key="ctrl+o")
    )
    lock_wallet: CliveBinding = field(default_factory=lambda: CliveBinding(id="lock_wallet", key="ctrl+l"))
    settings: CliveBinding = field(default_factory=lambda: CliveBinding(id="settings", key="ctrl+s"))
    switch_node: CliveBinding = field(default_factory=lambda: CliveBinding(id="switch_node", key="ctrl+n"))
    transaction_summary: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="transaction_summary", key="ctrl+t")
    )
    quit: CliveBinding = field(default_factory=lambda: CliveBinding(id="quit", key="ctrl+q"))


@dataclass
class Dashboard(CliveBindingSection):
    operations: CliveBinding = field(default_factory=lambda: CliveBinding(id="operations", key="o"))
    switch_working_account: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="switch_working_account", key="w")
    )
    account_details: CliveBinding = field(default_factory=lambda: CliveBinding(id="account_details", key="d"))
    add_account: CliveBinding = field(default_factory=lambda: CliveBinding(id="add_account", key="a"))
    remove_account: CliveBinding = field(default_factory=lambda: CliveBinding(id="remove_account", key="r"))


@dataclass
class Help(CliveBindingSection):
    toggle_help: CliveBinding = field(default_factory=lambda: CliveBinding(id="toggle_help", key="f1,?"))
    toggle_table_of_contents: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="toggle_table_of_contents", key="t")
    )


@dataclass
class ManageKeyAliases(CliveBindingSection):
    add_new_alias: CliveBinding = field(default_factory=lambda: CliveBinding(id="add_new_alias", key="a"))
    load_from_file: CliveBinding = field(default_factory=lambda: CliveBinding(id="load_from_file", key="l"))


@dataclass
class Operations(CliveBindingSection):
    add_to_cart: CliveBinding = field(default_factory=lambda: CliveBinding(id="add_to_cart", key="a"))
    finalize_transaction: CliveBinding = field(default_factory=lambda: CliveBinding(id="finalize_transaction", key="f"))
    witness_show_details: CliveBinding = field(default_factory=lambda: CliveBinding(id="witness_show_details", key="d"))


@dataclass
class TransactionSummary(CliveBindingSection):
    broadcast: CliveBinding = field(default_factory=lambda: CliveBinding(id="broadcast", key="b"))
    save_transaction_to_file: CliveBinding = field(
        default_factory=lambda: CliveBinding(id="save_transaction_to_file", key="s")
    )
    update_metadata: CliveBinding = field(default_factory=lambda: CliveBinding(id="update_metadata", key="u"))
