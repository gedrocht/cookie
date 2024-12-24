from config import _DEBUG_MODE, LOG_ROLLED_PROMPT_PARAMS, LOG_GENERATED_TEXT, _AI_OPTION_OPENAI, _AI_OPTION_GEMINI, _AI_OPTION_PAWANKRD, _AI_OPTION_GROQ, _AI_BEING_USED
from utils import roll, pick, join, select_portion_of_text

def _SUMMARIZER(): # Your summary will be rewritten in your own words.
    log_output = ""
    if LOG_ROLLED_PROMPT_PARAMS:
        log_output += "[SUMMARIZER] - "
    output = f"You are are a summarizing machine that will take a short segment of a story and summarize it in 3 to 6 sentences. "
    output += "If an event in the story you have been given was described as being resolved or otherwise dealt with, do not mention it in your summary at all. "
    output += "The story should focus exclusively on two to three ongoing events. "
    output += "Slightly alter story threads to relate them together with one another. "
#    output += "Any story element that seems silly, alter the story element so that it is more serious and frightening. "
    output += "The events you describe must be relevant to the population at large, the general public. "

    if _AI_BEING_USED == _AI_OPTION_GEMINI:
        output += 'Do not use placeholder statements like "insert advice". instead, write the actual thing that should be inserted. '
        output += 'Do not use placeholders like "your name", write the actual thing that should be written. '

    summary_resolution = pick([
        "mix it in with another different plot point, combining the two somehow",
        "omit it from your summary (if it's minor or seems close to being resolved)",
        "choose a different plot point and explain how the two cancelled each other out",
        "omit it from your summary"])

    output += f"If the summary you are given contains more than 3 ongoing events, {summary_resolution}. "
    output += "If two events are very similar, combine them into one event. "

    if LOG_ROLLED_PROMPT_PARAMS:
        log_output += f"CURTAILMENT: {summary_resolution}"

    if roll(0.5):
        summary_change = pick([ \
            "deescalate it towards resolution",
            "add an unexpected twist, complicating things",
            "escalate it, making the situation more threatening",
            "mix it in with another different plot point, combining the two somehow",
            "omit it from your summary if it's minor or close to being resolved",
            "reveal something about it and add what was revealed to your summary",
            "choose a different plot point and explain how the two cancelled each other out",
            "omit it from your summary"
        ])
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f", CHANGE: {summary_change}"
        output += f"You will choose a single plot point at random, and you will {summary_change}."
    
    output += f"Your response must only contain the summary. "

    print(log_output.replace("\n","").replace("\r",""))
    return output