from utils import pick, roll
from config import _DEBUG_MODE, LOG_ROLLED_PROMPT_PARAMS, LOG_GENERATED_TEXT, _AI_OPTION_OPENAI, _AI_OPTION_GEMINI, _AI_OPTION_PAWANKRD, _AI_OPTION_GROQ, _AI_BEING_USED

def _ACTION_TAKER():
    actor_role = pick(["first responder", "random citizen"])
    actor_impact = pick(["nearly invisible", "minimal", "very small", "small", "somewhat small", "moderate", "notable", "sizeable", "somewhat large", "very large", "huge", "decisive"])
    if LOG_ROLLED_PROMPT_PARAMS:
        print("----------------------------------")
        print(f"CITIZEN")
        print(f"\tROLE: {actor_role}")
        print(f"\tIMPACT: {actor_impact}")

    output = f"You are a {actor_role} in the middle of an evolving crisis. "
    output += "You will be given an emergency broadcast containing a description of the situation and instructions for safety. "
    output += "You will decide on a course of action to take given this information. "
    output += f"Your action will have a {actor_impact} impact on the situation. "
    # output += "You will describe what happens as a result of you taking this {actor_impact} action. "
    output += "Your report will be in first-person, referring to yourself as 'I'. "
    output += "Your response will contain only your intended plan of action. "
    return output
