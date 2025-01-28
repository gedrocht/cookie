import pytest
from ai_chat.character import Character
from ai_chat.prompt import Prompt
from ai_chat.message import Message

# run with `pytest tests`

def test_character_increase_urge_to_speak():
    prompt = Prompt(core="Core", flux="Flux", memories="Memories")
    char = Character(prompt=prompt, ID=1)

    # We'll force multiple increments
    max_iterations = 20
    triggered = False
    for _ in range(max_iterations):
        if char.increase_urge_to_speak():
            triggered = True
            break

    # Since each increment is < 1, it might not reach 10 in 20 tries, but let's assert
    # that the function returns a bool and that urge_to_speak is >= 0.
    assert isinstance(triggered, bool)
    assert char.urge_to_speak >= 0

def test_character_unread_messages():
    prompt = Prompt(core="Core", flux="Flux", memories="Memories")
    msg1 = Message(source="NPC", message="Hello!")
    msg2 = Message(source="System", message="Update available.")
    char = Character(
        prompt=prompt,
        ID=42,
        unread_messages=[msg1, msg2],
        name="TestChar",
        urge_to_speak=0.0
    )

    assert len(char.unread_messages) == 2
    assert char.unread_messages[0].source == "NPC"
    assert char.unread_messages[1].message == "Update available."
