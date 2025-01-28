import pytest
from ai_chat.message import Message

# run with `pytest tests`

def test_message_fields():
    msg = Message(source="User", message="Hello, World!")
    assert msg.source == "User"
    assert msg.message == "Hello, World!"
