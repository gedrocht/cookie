from ai_chat.prompt import Prompt
from ai_chat.message import Message
from ai_chat.character import Character

prompt_instance = Prompt(core="CoreValue", flux="FluxState", memories="SomeMemories")
message_one = Message(source="NPC", message="Hello traveler!")
message_two = Message(source="System", message="Quest update available.")

char = Character(
    prompt=prompt_instance,
    ID=1,
    unread_messages=[message_one, message_two],
    name="Hero",
    urge_to_speak=0.0
)

# Use the prompt's function
print(prompt_instance.build_prompt())

# Increase urge_to_speak
for i in range(15):
    is_10_or_more = char.increase_urge_to_speak()
    print(f"New urge_to_speak: {char.urge_to_speak} -> Above 10? {is_10_or_more}")
    if is_10_or_more:
        print("The urge_to_speak has reached 10 or more!")
        break
