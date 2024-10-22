"""Custom exceptions mainly used for very specific control flow."""

from __future__ import annotations


class NotFoundError(Exception):
    """Exception raised when a zettel cannot be found."""


class NotEnteredError(Exception):
    """Exception raised when ID wasn't provided."""
