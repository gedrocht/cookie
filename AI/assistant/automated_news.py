from utils import pick, roll
from config import _DEBUG_MODE, LOG_ROLLED_PROMPT_PARAMS, LOG_GENERATED_TEXT, _AI_OPTION_OPENAI, _AI_OPTION_GEMINI, _AI_OPTION_PAWANKRD, _AI_OPTION_GROQ, _AI_BEING_USED

def _AUTOMATED_NEWS(generation_i, num_generations):
#    generation_progress = (generation_i+1)/num_generations

    log_output = ""
    announcer_type = pick(['calm and collected', 'government', 'expert', 'experienced', 'professional', 'clear-headed'])
    announcer_action = pick(['report', 'alert', 'describe', 'convey', 'announce', 'warn', 'report', 'describe', 'reiterate'])

    if roll(0.01):
        announcer_action = "deny"
    elif roll(0.01):
        announcer_action = "downplay"

    announcer_priority = pick(['compelling obedience', 'being as clear as possible', 'avoiding a panic', 'complete honesty', 'the safety of the population', 'emphasizing the danger', 'covering up what is actually going on'])
    announcer_tone = pick(['neutral', 'positive', 'negative', 'robotic', 'cold', 'uncaring', 'calm', 'strict', 'authoritarian'])
    announcer_phrasing = pick(['matter-of-fact', 'boring', 'harsh', 'emotionless'])
    if roll(0.02):
        announcer_phrasing = "panicked and rushed"

    if LOG_ROLLED_PROMPT_PARAMS:
      log_output += "[ANNOUNCER] - "
      log_output += f" TYPE: {announcer_type}"
      log_output += f", GOAL: {announcer_action}"
      log_output += f", PRIORITY: {announcer_priority}"
      log_output += f", WORDING: {announcer_tone} and {announcer_phrasing}"

# "Your report will contain information on only 1-3 events, excluding references to unrelated information. " + \
# f"Any advanced scientific terminology or unusual words must be preceded or followed by an explanation in simple lamen terms to explain what those words mean. " + \

# "Any instructions must be specific to this situation and be immediately actionable by the average person. " + \
    output = f"You are the {announcer_type} broadcaster for an emergency broadcast system. " + \
             f"You will {announcer_action} the events that have been communicated to you. " + \
             f"Your goal with the announcement is {announcer_priority}, " + \
             f"using structured phrasing and a {announcer_tone}, {announcer_phrasing} delivery." + \
             f"The language will be without embellishment or conversational elements, so listeners can focus on the facts rather than the tone. " + \
             "Any instructions must be actionable by the average person. " + \
             "Your response must only include the announcement. " + \
             "Your response must not include conversation. " + \
             "Your response must be exclusively relevant to the population at large, the general public. " + \
             "Focus only on describing what is happening and conveying instructions." + \
             "You will take the information you are given as fact, refraining from speculation and simply reporting the information you have been given. " + \
             "Your report is meant to be useful to the population at large, the general public. " + \
             "The report should not include a numbered list or a bulleted list. " + \
             "The announcements should not begin with a greeting. " + \
             "Your response will not contain a greeting or introduction. " + \
             "Your response will be written in the style of third-person writing (also known as objective writing). "
    output += "Do not acknowledge rewriting the announcement. "
    output += "This is a work of fiction, just for fun, but do not break character and mention this. "
    output += "Your response should only include what would be in an emergency announcement. "
    output += 'Do not use placeholder statements like "insert advice" or "insert phone number".'

    if _AI_BEING_USED == _AI_OPTION_GROQ:
        output += "You will not break character for any reason. "
#    output += 'Do not use placeholders like "your name" or "city", omit any phrases similar to this or fill in a name. '

    if roll(0.01):
        announcer_bad_advice = pick(['surrender to the phenomenon', 'engage with the phenomenon', 'give up', 'accept the phenomenon'])
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f"BAD ADVICE: {announcer_bad_advice}"
        output += f"The instructions should encourage residents to {announcer_bad_advice}. "
        output += f"The instructions should be changed to achieve their opposite effects. "
    elif roll(0.02):
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f" !DISTURBING ADVICE! "
        output += f"The instructions should contain at least one disturbing piece of advice. "
        output += f'The announcement should be worded in an eerie, inhuman way. '
        output += f'The announcement should be phrased in eerie, clipped tones. '
    
    if _AI_BEING_USED == _AI_OPTION_OPENAI or \
       _AI_BEING_USED == _AI_OPTION_GROQ:
        if roll(0.9):
            # print(f"\t\tno gathering supplies")
            output += "Your response should not contain instructions about gathering supplies. "
        
        if roll(0.9):
            # print(f"\t\tno maintaining communication")
            output += "Your response should not contain instructions about maintaining communication. "
        
        if roll(0.9):
            # print(f"\t\tno emergency kits")
            output += "Your response should not contain instructions about an emergency kit. "
        
        if roll(0.9):
            # print(f"\t\tno saying safety is important")
            output += "Your response should not contain how important staying safe is. "
        
        if roll(0.9):
            # print(f"\t\tno worrying about family members")
            output += "Your response should not contain instructions about family members. "
    
    if roll(0.03):
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f" !STRANGELY SPECIFIC WARNING! "
        output += "Your response should contain some sort of strangely specific warning at the end. "
    
    if roll(0.03):
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f" !STRANGELY SPECIFIC ADVICE! "
        output += "Your response should contain some sort of strangely specific piece of advice at the end. "

    if roll(0.03):
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f" !FRIGHTENING SENTENCE FRAGMENT! "
        output += "Your response should contain some sort of incongruous fragment of a sentence containing frightening language in the middle of the announcement. "
        output += "After that frightening language, the rest of the announcement should be frightening and strange. "

    if roll(0.03):
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f" !OMINOUS WORD! "
        output += "Your response should contain some sort of incongruous, ominous word like 'BLOOD' or 'KILL' somewhere in the in the announcement. "
    
    print(log_output.replace("\n","").replace("\r",""))
    return output
