
from config import _DEBUG_MODE, LOG_ROLLED_PROMPT_PARAMS, LOG_GENERATED_TEXT, _AI_OPTION_OPENAI, _AI_OPTION_GEMINI, _AI_OPTION_PAWANKRD, _AI_OPTION_GROQ, _AI_BEING_USED
from utils import roll, pick, join, select_portion_of_text

def _STORYTELLER(_MOODS, _PLOT_MOODS, _PLOTS, _STAKES, _SUBPLOTS, _SUBPLOT_STAKES_BEGINNINGS, _SUBPLOT_STAKES_ENDS, _STAKE_MULTIPLIERS):
    log_output = ""
    if LOG_ROLLED_PROMPT_PARAMS:
        log_output += "[STORYTELLER] - "

    story_plot_mood = pick(_PLOT_MOODS)
    story_plot = pick(_PLOTS)
    story_stakes = pick(_STAKES)
    story_subplot = pick(_SUBPLOTS)
    story_subplot_stakes = f"{pick(_SUBPLOT_STAKES_BEGINNINGS)} {pick(_SUBPLOT_STAKES_ENDS)}"
    story_subplot_stakes = f"{pick(_SUBPLOT_STAKES_ENDS)}"
    story_portion = pick(['All', 'Some', 'No', 'Nearly all', 'None of the', 'Some of the', 'Half of the'])
    story_mood = pick(_MOODS)
    story_stake_multiplier = pick(_STAKE_MULTIPLIERS)

    if LOG_ROLLED_PROMPT_PARAMS:
        log_output += f"PLOT: {story_plot_mood} {story_plot}"
#    print(f"\tSUBPLOT: {story_subplot_stakes} {story_subplot}")
# f"with {story_subplot_stakes} {story_subplot} . " + \
        log_output += f", STAKES: {story_stakes}"
        log_output += f", DETAIL: {story_portion} new events should have {story_mood}"
#    print(f"\tINTENSITY: {story_stake_multiplier}")
#             f"The events in the story will be {story_stake_multiplier}. " + \


#             "The new part of the report will be a minimum of 3 sentences and a maximum of 5 sentences. " + \

    num_simultaneous_events = 3
    if _AI_OPTION_GROQ:
        num_simultaneous_events = 2
    if _AI_OPTION_PAWANKRD:
        num_simultaneous_events = 1
#             f"The situation is volatile and is changing at a rate which is {story_stake_multiplier}. " + \
    output = "You are a reporter continuing a report from the previous part, which you will be given. " + \
             f"The story will involve mysterious {story_plot_mood} {story_plot} " + \
             f"Introduce unexpected developments that are at least vaguely related to the current situation, causing {story_stakes}. " + \
             f"{story_portion} new events should be at least vaguely related to the situation and have " + \
             f"{story_mood}. " + \
             "The report will update the events from the previous part, developing and changing the situation and potentially resolving plot points. " + \
             f"All story events must be related somehow. " + \
             f"The story should be written as though everything was normal but now there is an emergency. " + \
             f"The story should focus on a maximum of {num_simultaneous_events} ongoing phenomena. " + \
             f"In the event of more than {num_simultaneous_events} ongoing phenomena, describe the resolution of one them. " + \
             "The story should be written in present-tense. " + \
             f"Focus on large groups of multiple people. "
    if _AI_BEING_USED == _AI_OPTION_GEMINI:
        output += 'Do not use placeholders like "your name", write the actual thing that should be written. '
    if _AI_BEING_USED == _AI_OPTION_GROQ:
        output += "Events you mention must be relevant to the population at large. "
        output += 'Do not use placeholder statements like "insert advice". instead, write the actual thing that should be inserted.'
        output += 'Do not mention the quality of the report. '
        output += 'Do not mention information sources. '
        output += 'Do not mention misinformation. '
        output += 'Do not mention rumors. '
        output += 'Do not mention official channels. '
        output += 'Your report should be at least vaguely unsettling. '
    print(log_output.replace("\n","").replace("\r",""))
    return output

'''
             "You will be given the plan of a random unnamed person in the story, their reaction to what little they understand. " + \
             "The new part of the story will update the previous events given the effect that person's plan might have on those events. " + \
             "The new part of the story will also update in ways that are unrelated to the effects of the random person's plan. " + \
'''
