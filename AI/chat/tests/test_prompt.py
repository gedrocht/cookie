import pytest
from ai_chat.prompt import Prompt

# run with `pytest tests`

def test_prompt_build_prompt():
    prompt = Prompt(core="Core", flux="Flux", memories="Memories")
    result = prompt.build_prompt()
    assert result == "Core Flux you remember Memories"
