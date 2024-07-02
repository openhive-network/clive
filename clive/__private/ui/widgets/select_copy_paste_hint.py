from __future__ import annotations

from textual.widgets import Static

from clive.__private.ui.widgets.clive_collapsible import CliveCollapsible


class SelectCopyPasteHint(CliveCollapsible):
    def __init__(
        self,
        *,
        title: str,
        system_color: str,
        shortcut_styling: str,
        collapsed: bool = True,
        collapsed_symbol: str = "▶",
        expanded_symbol: str = "▼",
        name: str | None = None,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        description = f"""\
To select some text hold [{shortcut_styling}]Shift[/] while you click and drag.

Copy/Paste action shortcuts depend on the environment and you may check:
  > On [{system_color}]Linux[/]: [{shortcut_styling}]Ctrl+Shift+C[/] / [{shortcut_styling}]Ctrl+Shift+V[/]
  > On [{system_color}]Windows[/]: [{shortcut_styling}]Ctrl+C[/] / [{shortcut_styling}]Ctrl+V[/]
If none of the above works, you may also try [{shortcut_styling}]Ctrl+Insert[/] / [{shortcut_styling}]Shift+Insert[/].
More info can be found on the Help page.\
"""
        super().__init__(
            Static(description),
            title=title,
            collapsed=collapsed,
            collapsed_symbol=collapsed_symbol,
            expanded_symbol=expanded_symbol,
            name=name,
            id=id_,
            classes=classes,
            disabled=disabled,
        )
