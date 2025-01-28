from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Message:
    """
    Represents a message with a source string and a message string.
    """

    source: str
    message: str
