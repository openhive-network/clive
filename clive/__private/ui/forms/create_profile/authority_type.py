from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Collapsible, Static


class AccountCollapsible(Collapsible):
    DEFAULT_CSS = """
    AccountCollapsible {        
        border-top: none;
        margin-bottom: 1;
    }
    AccountCollapsible.-collapsed{
        padding-bottom: 0;
    }
    """

class AuthorityType(Collapsible):
    DEFAULT_CSS = """
    AuthorityType {        
        border-top: none;
        margin-bottom: 1;
    }
    
    AuthorityType.-collapsed{
        padding-bottom: 0;
        height: 1;
    }
    
    Horizontal {
      width: 1fr;
      height: auto;

    }
    #horiz2 {
      align-horizontal: right;
        Static {
          align: right middle;
          width: auto;
          margin-right: 1;
        }

    }
    """

    def compose(self) -> ComposeResult:
        yield Horizontal(self._title, Horizontal(Static("threshold 1/1"), id="horiz2"))
        yield self.Contents(*self._contents_list)
