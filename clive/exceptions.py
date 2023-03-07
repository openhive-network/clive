from __future__ import annotations


class CliveError(Exception):
    """Base class for all clive exceptions."""


class NodeAddressError(CliveError):
    """Base class for all node address exceptions."""
