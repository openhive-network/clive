class CliveException(Exception):
    """Base class for all clive exceptions."""


class ViewException(CliveException):
    """Base class for all view exceptions."""


class ViewDoesNotExist(ViewException):
    """Raised when a view does not exist."""
