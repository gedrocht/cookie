from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List

from .prompt import Prompt
from .message import Message

@dataclass
class Character:
    """
    Holds a Prompt instance, an ID, a list of unread Message instances, a name,
    and an urge_to_speak float. It offers a method to increase the urge_to_speak
    by a random amount between 0 and 1.
    """

    prompt: Prompt
    ID: str
    unread_messages: List[Message] = field(default_factory=list)
    name: str = "Unnamed"
    voice: str = ""
    urge_to_speak: float = 0.0

    def increase_urge_to_speak(self) -> bool:
        """
        Increases the urge_to_speak by a random float in [0, 1).
        Returns True if urge_to_speak >= 10, else False.

        :return: bool
        """
        self.urge_to_speak += random.uniform(0, 1)
        return self.urge_to_speak >= 10
