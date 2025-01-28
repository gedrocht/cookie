
### 6.3 `src/ai_chat/__init__.py`

"""
ai_chat package

Expose the main classes here for convenience.
"""

from .prompt import Prompt
from .message import Message
from .character import Character

__all__ = [
    "Prompt",
    "Message",
    "Character"
]
