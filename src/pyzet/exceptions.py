"""Custom exceptions mainly used for very specific control flow."""
from __future__ import annotations


class NotFound(Exception):
    pass


class NotEntered(Exception):
    pass
