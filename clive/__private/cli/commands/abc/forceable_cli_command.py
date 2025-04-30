from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(kw_only=True)
class ForceableCLICommand:
    """A base class for CLI commands that can be forced to execute."""

    force: bool = field(default=False)
    """Whether to force the execution of the command."""
