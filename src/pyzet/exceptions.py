"""Custom exceptions mainly used for very specific control flow."""

from __future__ import annotations


class ZettelNotFoundError(Exception):
    """Exception raised when a zettel cannot be found."""
