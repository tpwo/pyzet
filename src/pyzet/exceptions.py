"""Custom exceptions mainly used for very specific control flow."""

from __future__ import annotations


class AbortError(SystemExit):
    """Exception raised when user aborts the app, usually with ^C."""

    def __init__(self) -> None:
        super().__init__('\naborting')


class ZettelNotFoundError(Exception):
    """Exception raised when a zettel cannot be found."""
