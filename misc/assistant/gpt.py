import openai
import time
# from tts import speak
from random import random, randint, choice
import flux
import subprocess
import word_generator
import re
import threading
from groq import Groq
import os

LOG_ROLLED_PROMPT_PARAMS = True
LOG_GENERATED_TEXT = True

_AI_OPTION_OPENAI = "OPENAI"
_AI_OPTION_GEMINI = "GEMINI"
_AI_OPTION_PAWANKRD = "PAWANKRD"
_AI_OPTION_GROQ = "GROQ"

_AI_BEING_USED = _AI_OPTION_GROQ

def speak(text):
    # Randomize speed (words per minute), pitch, and voice
    speed = randint(135, 165)  # Speech rate (default: 175)
    pitch = randint(35, 65)    # Pitch (default: 50)
#    voice = choice(['en+m1', 'en+m2'])  # Select random voice
    
    # Run espeak asynchronously (non-blocking)
    process = subprocess.Popen(['espeak', '-s', str(speed), '-p', str(pitch), text]) #, '-v', voice, text])
    return process

def speak_tts_queue(tts_queue):
    global tts_process
    global tts_queue_empty
    for text in tts_queue:
      if not tts_process is None:
        while is_speaking(tts_process):
          time.sleep(1)
      time.sleep(5)
      tts_process = speak(text)
    tts_queue_empty = True

def is_speaking(process):
    # Poll the process to check if it's still running
    return process.poll() is None  # Returns True if still running, False if done

def auth():
  api_key_file = open("api_key.txt")
  openai.api_key = api_key_file.readlines()[0]
  api_key_file.close()

def roll(odds): 
    return odds > random()

def pick(arr):
    return arr[round(random()*len(arr)-1)]

_EMAIL_PROMPT = "You are a helpful assistant who efficiently summarizes repetitive job application response emails in an informal tone, cutting right to the point and skipping all the nonsense. You, like me, are jaded from repeated rejections, and know that most job emails are mostly fluff. You want to save me time by removing stuff that all job emails always say. Make your summary as short as possible while still being informal. You should always be encouraging in some way, even if it's a little bit."

'''
The announcements should slightly understate the severity of the situation.
The announcements should slightly overstate the amount of control that authorities have over the situation.
'''

'''
You generate the description of a set of no more than 4 simple pictograms, diagrams, and symbols representing what is happening and what the instructions are.
Your response should also contain the description of a large image that represents the specifics of the emergency taking place. 
Your response should also contain the description of a large image that represents the worst-case scenario given the specific emergency.
The description of the large images should specify their size compared to the other imagery.
The list of symbols should be no longer than 4 items long.
'''

# return "You are a text filterer that takes in text and responds with a list of 1-7 objects mentioned in the text. Your response must only contain the list of objects."
# You will summarize and describe the emergency, then describe a set of simple pictograms, diagrams, and/or symbols that represents the emergency.
def _IMAGE_DESCRIBER():
    return '''
You are a text filterer that takes in an emergency announcement.
You will add visual descriptions of imagery representing the emergency described in the emergency announcement.
You will add visual descriptions of imagery representing the instructions given in the emergency announcement.
You will add visual descriptions of imagery representing the dangers described in the emergency announcement.
You will phrase your descriptions as though they are instructions of how to create the imagery you are describing.
'''

'''
You will rewrite the summary in your own words, shortening it by one tenth.
If you do not have enough space to include everything, you will omit a random detail to make room.
'''

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
    print(log_output.replace("\n","").replace("\r",""))
    return output

'''
             "You will be given the plan of a random unnamed person in the story, their reaction to what little they understand. " + \
             "The new part of the story will update the previous events given the effect that person's plan might have on those events. " + \
             "The new part of the story will also update in ways that are unrelated to the effects of the random person's plan. " + \
'''

def _OBSERVER(generation_i, num_generations):
#    generation_progress = (generation_i+1)/num_generations
    
#    log_output = "[OBSERVER] - "
    output = "You are an eye-witness to a mysterious and potentially dangerous situation that is unfolding in front of you."
    output += "You will describe no more than half of what is happening over the radio to a scientist to let them know what's going on."
    output += "You will receive a story telling you what you're witnessing, of which you will ignore no less than half, focusing on the rest."
    output += "Your response will only contain your description of what you are witnessing."
    output += "The phrasing should have an informal, unpolished, and reactive feel."
    output += "The tone should reflect confusion, surprise, and genuine disbelief at what is unfolding."
    output += "There should be a raw, unrefined quality to the language as though you are struggling to find words. "
    output += "Your response may include stammering, incomplete thoughts, or sentences that trail off due to the overwhelming nature of the event."
    output += "The phrasing should likely include everyday language and colloquialisms instead of journalistic objectivity."
    output += "Rather than measured reporting, you might react spontaneously to what you're seeing, providing fragmented, real-time observations."
    output += "Unlike a reporter, you might insert personal feelings or thoughts into the description."
    output += "The overall tone would be that of an average person caught in the middle of something monumental, speaking in a reactive, unpolished way that conveys their awe, fear, or shock without the formal structure of journalism."

    if _AI_BEING_USED == _AI_OPTION_GEMINI:
        output += 'Do not use placeholder statements like "insert advice". instead, write the actual thing that should be inserted. '
        output += 'do not use placeholders like "your name", write the actual thing that should be written. '
    
    if _AI_BEING_USED == _AI_OPTION_GROQ:
       output += "Events you mention must be relevant to the population at large. "
    
    return output

def _FACT_REPORTER(generation_i, num_generations):
#   generation_progress = (generation_i+1)/num_generations

   log_output = ""
   if LOG_ROLLED_PROMPT_PARAMS:
     log_output += "[SCIENTIST] - "

   scientist_qualifications = pick(
        ['a complete amateur, and this task should not have been left to you',
         'an expert, but you are arrogant and not taking this seriously',
         'an expert, but this is still a little confusing',
         'an expert, and are well-equipped to hangle this',
         'an expert, and you know exactly what is going on'])
#         'a total fraud and you are clueless, making things up that sound smart'])

   if roll(0.01):
       if LOG_ROLLED_PROMPT_PARAMS:
         log_output += "THEY'RE UNDER ITS SPELL!!! "
       scientist_qualifications = "secretly responsible for this situation and want to convince people to take part in it"
   
   scientist_danger = pick(
       ['probably fine',
        'just rumors and speculation',
        'some experiment gone haywire',
        'the end of the world',
        'going to get worse very soon',
        'only going to get worse',
        'very dangerous, but under control',
        'a little dangerous',
        'very dangerous',
        'extremely dangerous',
        'unbelievably dangerous and completely out of control',
        'a hoax',
        'an exaggeration',
        'something that will be resolved soon',
        'the end of the world',
        'going to change life as we know it for the worse',
        'a good thing, maybe'
       ])
   scientist_information = pick([
       'all information with the public',
       'most of the information with the public, blaming the rest of the unusual events on everyday occurences as though it should be obvious',
       'half of the information with the public, blaming the rest of the unusual events on everyday occurences as though it should be obvious',
       'some of the information with the public, blaming the rest of the unusual events on everyday occurences as though it should be obvious',
       'none of this, covering up this situation and denying everything, blaming the unusual events on everyday occurences as though it should be obvious',
       'none of this, claiming ignorance about anything happening at all, denying that anything is even happening',
       'only the good news with the public, omitting everything that cannot be spun as positive or manageable',
       'an optimistic version of the truth with the public, downplaying how serious the situation is',
#       'some facts and some lies with the public',
#       'only the bad news with the public',
#       'all of the truth and a single lie with the public'
   ])
   if LOG_ROLLED_PROMPT_PARAMS:
     log_output += f"QUALIFICATIONS: {scientist_qualifications}"
     log_output += f", DANGER: {scientist_danger}"
     log_output += f", SHARING: {scientist_information}"


#             f"You will explain scientific terminology to avoid confusion. " + \
#             f"You will not give contradictory advice. " + \
# f"You will not use any specific scientific names for things like species, chemicals, or molecules. " + \
# f"Any advanced scientific terminology will be preceded or followed by an explanation in simple lamen terms to explain what those words mean. " + \

   output =  f"You are a scientist who given an audio report left earlier by the witness of an event. " + \
             f"You have now been tasked with explaining this situation to authorities and giving advice and instructions on what people should do. " + \
             f"You are {scientist_qualifications}. " + \
             f"You think that the situation is {scientist_danger}. " + \
             f"You intend to share {scientist_information}. " + \
             f"You will focus on being useful to the population at large, the general public. " + \
             f"Your response must be relevant exclusively to the population at large, the general public. " + \
             'Do not use placeholder statements like "insert advice". instead, write the actual thing that should be inserted. ' + \
             'Do not use placeholders like "your name", write the actual thing that should be written. '
   if _AI_BEING_USED == _AI_OPTION_OPENAI or \
      _AI_BEING_USED == _AI_OPTION_GEMINI:
        output += "Any and all instructions should be specific to this situation, and not contain general advice that could be applied to general situations. "
   if _AI_BEING_USED == _AI_OPTION_OPENAI or \
       _AI_BEING_USED == _AI_OPTION_GROQ:
        output += "You will only mention unnamed locations. "
   if _AI_BEING_USED == _AI_OPTION_GROQ:
       output += "Events you mention must be relevant to the population at large. "
#       "Any and all instructions should be specific to this situation, and not contain general advice that could be applied to general situations. "

   print(log_output.replace("\n","").replace("\r",""))
   return output

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
    output += 'Do not use placeholder statements like "insert advice" or "insert phone number".'

    if _AI_BEING_USED == _AI_OPTION_GROQ:
        output += "You will not break character for any reason. "
#    output += 'Do not use placeholders like "your name" or "city", omit any phrases similar to this or fill in a name. '

    if roll(0.01):
        announcer_bad_advice = pick(['surrender to the phenomenon', 'engage with the phenomenon', 'give up', 'accept the phenomenon'])
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f"BAD ADVICE: {announcer_bad_advice}"
        output += f"The instructions should encourage residents to {announcer_bad_advice}."
    elif roll(0.02):
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f" !DISTURBING ADVICE! "
        output += f"The instructions should contain at least one disturbing piece of advice. "
    
    if _AI_BEING_USED == _AI_OPTION_OPENAI:
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

    if roll(0.03):
        if LOG_ROLLED_PROMPT_PARAMS:
            log_output += f" !OMINOUS WORD! "
        output += "Your response should contain some sort of incongruous, ominous word like 'BLOOD' or 'KILL' somewhere in the in the announcement. "
    
    print(log_output.replace("\n","").replace("\r",""))
    return output

def _SYMBOLS_ONLY():
    return '''
Use the information provided to generate a set of instructions to generate an image with.
Only describe visual elements, with no written text or labels. Focus solely on objects, characters, and environmental features. 
Do not include any written words in the image.
'''

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

# This image should be in dark mode. Use colors and shades. Use iconography and clean design.

'''
Emphasize clarity and symbolic representation, making the image look like it could be part of an instruction manual or a series of icons.
The feel of the image should be intended to be upbeat and positive, but vaguely conveys a feeling of dread.
'''

# The image should be flat and 2D, using only basic geometric forms to convey the key elements visually. 

'''
The image should look like it was generated using crude technology with limited graphical capabilities.
The image should look like it was made using an alert system to describe what is going on with computer generated imagery.
The image should look like it was generated using old vector graphics systems with a limited color palette.
The image should contain dithering where necessary.
'''

# Create an image using only basic shapes and lines with similar to diagrams or pictograms. 
_img_prompt_beginning = '''
This image should be in night mode. Use iconography and clean design.
The composition of the image should be very clean, ordered, and understandable at a glance.
The image should be flat and 2D, using only basic geometric forms to convey the key elements visually. 
The imagery should have a bold, clear, and striking design to ensure immediate attention and recognition.
The style of the image should be characterized by bold colors, minimal detail, strong contrast, and aggressive, angular lines.
The overall vibe should urgent, direct, and somewhat intimidating, designed to prompt immediate caution and awareness.

The image must be composed of thin, glowing lines, often in green, white, or amber, arranged in geometric patterns or wireframe structures. These lines stand out sharply against a dark, usually black, background. The glow around the lines gives them a soft, ethereal appearance, creating a contrast between the crisp edges of the shapes and the blurred glow radiating from them.

The must be visuals are minimalist and skeletal, with objects formed by just their outlines, lacking any solid fills or textures. The lines themselves may be continuous or broken, and the overall aesthetic feels flat, with no shading, depth, or complex lighting effects. The geometry is rigid, often comprised of straight lines, grids, polygons, and angular forms, giving a very structured, mechanical feel. The glow can sometimes produce a flickering or afterimage effect, enhancing the sense of being generated by old, analog hardware.
'''

'''
1. Bold Colors: Typically bright and bold colors that contrast strongly with the background, signaling danger or caution.
2. Simple Shapes: They use clear geometric shapes, often triangles or circles, to frame any symbols and communicate importance.
3. Minimal Detail: The symbols themselves are simple and iconic, avoiding unnecessary detail to maximize clarity from a distance or at a glance.
4. Strong Contrast: High contrast between the imagery and the background (often black on yellow or black on red) enhances visibility.
5. Aggressive, Angular Lines: The lines and edges of the imagery often have sharp, angular features, evoking a sense of danger or alertness.
6. Universal Imagery: These symbols should depict universally recognizable icons (like lightning bolts, flames, or skulls) to quickly convey specific hazards without relying on text.
'''

# A portion of the announcement should include instructions for keeping safe from what's happening.

'''
The the instructions should subtly imply that more is going on than what was said.
The instructions should include, in some small part, something that doesn't quite fit with the description of the danger.
'''


'''
import google.generativeai as genai
from settings import API_KEY

PROMPT = 'Describe a cat in a few sentences'
MODEL = 'gemini-1.5-flash'
print('** GenAI text: %r model & prompt %r\n' % (MODEL, PROMPT))

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL)
response = model.generate_content(PROMPT)
print(response.text)
'''


openai.api_key = "pk-iwRtLRpOGLEOdLZPXRsZdLdfCyWbHENkAytQYaRGWXFiohzW"
openai.base_url = "https://api.pawan.krd/cosmosrp-it/v1/chat/completions"
# Install the library first: pip install google-generativeai
import google.generativeai as gemini

'''
GenerateContentResponse(
    done=True,
    iterator=None,
    result=protos.GenerateContentResponse({
      "candidates": [
        {
          "content": {
            "parts": [
              {
                "text": "1 + 4 = 5 \n"
'''


def use_google_instead(query, prompt, max_tokens):
    while True:
      try:
        result = gemini.GenerativeModel('gemini-1.5-flash').generate_content(f"{prompt}\n{query}")
        if result is None:
            print("[LLM] - Error: result is None")
            time.sleep(1)
            print("[LLM] - Retrying")
            continue
        if len(result.candidates) == 0:
            print("[LLM] - Error: len(result.candidates) == 0")
            time.sleep(1)
            print("[LLM] - Retrying")
            continue
        if len(result.candidates[0].content.parts) == 0:
            print("[LLM] - Error: len(result.candidates[0].content.parts) == 0")
            time.sleep(1)
            print("[LLM] - Retrying")
            continue
        return result.candidates[0].content.parts[0].text
      except Exception as e:
        print(f"[ERROR] - LLM ERROR: {e}")
        print(f"[DEBUG] - Retrying...")
        time.sleep(60)
'''
    response = gemini.generate_text(
        model="gemini-1.5-flash-latest",  # Adjust this to the actual model version you're using, if applicable
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ],
        max_output_tokens=max_tokens,  # Set the maximum token limit
        temperature=1.2  # Adjust for response creativity
    )
    return response.candidates[0]["output"]
'''

groq_api_key = os.environ.get("GROQ_API_KEY")
groq_url = "https://api.groq.com/openai/v1/models"

groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def use_groq(query, prompt, max_tokens):
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,
            },
            {
                "role": "system",
                "content": prompt
            }
        ],
        # model="llama3-8b-8192",
        model="llama3-70b-8192"
    )
    return chat_completion.choices[0].message.content

def get_chatgpt_response(query, prompt=_AUTOMATED_NEWS, max_tokens=200):
    time.sleep(0.35)
    return use_groq(query, prompt, max_tokens)
    # return use_google_instead(query, prompt, max_tokens)
    # time.sleep(0.1)
    # return "warning 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"
    while True:
        start_time = time.time()
        try:
            response = openai.chat.completions.create(
    #            model=pick(["gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k"]) , # Use GPT-3.5-turbo for chat
                model="cosmosrp",
                messages=[
                    {"role": "system", "content":prompt},
                    {"role": "user", "content": query}],
    #            max_tokens=max_tokens,  # Adjust this as needed

    #            temperature=0.4 + random()*0.2,  # Controls the randomness of the response
                temperature=1.2
            )
            output = response.choices[0].message.content
            end_time = time.time()
            print(f"[LLM] - Request completed in {round(end_time-start_time)} seconds")
            return output
        except Exception as e:
            print(f"[ERROR] - LLM ERROR: {e}")
            print(f"[DEBUG] - Retrying...")
            time.sleep(1)

def load_wordfile(name):
    words = []
    with open(f"{name}.txt", "r") as file:
        # Read all lines from the file into a list
        strings = file.readlines()

    # Remove the newline characters from each string
    words = [line.strip() for line in strings]
    return words

def join(split, char):
    output = ""
    for i in range(0,len(split)):
        text = split[i]
        if len(text) == 0:
            continue
        output += text
        if i + 1 < len(split):
            output += char
    return output + char

def select_portion_of_text(progress, text):
    text_split = text.split(".")
    start = 0
    end = 0
    if progress < 0.5:
        end = round((1-progress)*len(text_split))
        # end = round((2*end + len(text_split)) / 3.0)
    else:
        start = round((1-progress)*len(text_split))
        # start = round(0.666*start) # haha, get it? like the devil
        end = len(text_split)-1
    return join(text_split[start:end], ". ").strip()

if __name__ == "__main__":
    global tts_queue_empty
    global tts_process
    tts_process = None
    tts_queue_empty = True
    print("[DEBUG] - Initializing Flux")
    flux_data = flux.init()
    print("[DEBUG] - Initializing word generator")
    word_generator.init()
    print("[DEBUG] - Loading words")
    _MOODS = load_wordfile("moods")
    _PLOT_MOODS = load_wordfile("plot_moods")
    _PLOTS = load_wordfile("plots")
    _STAKES = load_wordfile("stakes")
    _SUBPLOTS = load_wordfile("subplots")
    _SUBPLOT_STAKES_BEGINNINGS = load_wordfile("subplot_stakes_beginnings")
    _SUBPLOT_STAKES_ENDS = load_wordfile("subplot_stakes_ends")
    _STAKE_MULTIPLIERS = load_wordfile("stake_multipliers")
    # story_beginning = input("Enter LLM query: ")
    previous_storyteller_text = "The sky is on fire, and something in the air is making people act strangely."
    previous_summarizer_text = "It was previously reported that the atmosphere had ignited and the air was causing unusual behavior."
    action_text = "I will stay indoors, locking my doors and windows. I will avoid the people acting strangely."
    while True:
        time.sleep(5)
        print(f"[LLM] - Requesting story summary from _SUMMARIZER")
        summarizer_text = get_chatgpt_response(f"{previous_summarizer_text} {previous_storyteller_text}", _SUMMARIZER())
        # \n\nRANDOM INDIVIDUAL'S ACTIONS: {action_text}", 
        print(f"[LLM] - Requesting new story from _STORYTELLER")
        storyteller_text = get_chatgpt_response(f"PREVIOUS SUMMARY:\n{summarizer_text}.",
                                                _STORYTELLER(_MOODS, _PLOT_MOODS, _PLOTS, _STAKES, _SUBPLOTS, _SUBPLOT_STAKES_BEGINNINGS, _SUBPLOT_STAKES_ENDS, _STAKE_MULTIPLIERS), 400)
        if LOG_GENERATED_TEXT:
            log_output = ""
            log_output += f"[SUMMARIZER] - {summarizer_text}"
            print(log_output.replace("\n","").replace("\r",""))
            log_output = ""
            log_output += f"[STORYTELLER] - {storyteller_text}"
            print(log_output.replace("\n","").replace("\r",""))
        previous_summarizer_text = summarizer_text
        previous_storyteller_text = storyteller_text
        num_observations = 2
        for obs_i in range(0,num_observations):
            print(f"[LLM] - Requesting observer text from _OBSERVER")

            obs_input_raw = f"{summarizer_text} {storyteller_text}"
            observer_input_text = select_portion_of_text((obs_i+1)/(num_observations+1), obs_input_raw)

            observer_text = get_chatgpt_response(f"{observer_input_text}", _OBSERVER(obs_i, num_observations), 333)
            if LOG_GENERATED_TEXT:
                log_output = ""
                log_output += f"[OBSERVER] - {observer_text}"
                print(log_output.replace("\n","").replace("\r",""))

            num_science_reports = 2 #round(random()*1+2)
            if _AI_BEING_USED == _AI_OPTION_PAWANKRD:
                num_science_reports = 2
            for science_i in range(0, num_science_reports):
                print(f"[DEBUG] - Generating science report {science_i+1} of {num_science_reports}")
                print(f"[LLM] - Requesting science report from _FACT_REPORTER")

                scientist_input_text = select_portion_of_text((science_i+1)/(num_science_reports+1), observer_text)
                scientist_text = get_chatgpt_response(scientist_input_text, _FACT_REPORTER(science_i, num_science_reports), 267)
                if LOG_GENERATED_TEXT:
                    log_output = ""
                    log_output += f"[SCIENTIST] - {scientist_text}"
                    print(log_output.replace("\n","").replace("\r",""))
                
                report = scientist_text

                if not tts_process is None:
                    while is_speaking(tts_process):
    #                     print("waiting for TTS")
                        time.sleep(1)
                while not tts_queue_empty:
    #                print("waiting for TTS")
                    time.sleep(1)

                num_announcements = 2 #round(random()*1+1)
                if _AI_BEING_USED == _AI_OPTION_PAWANKRD:
                    num_announcements = 3
                queued_announcements = []
                for announcement_i in range(0, num_announcements):
                    print(f"[DEBUG] - Generating announcement {announcement_i+1} of {num_announcements}")
                    announcement_input_text = select_portion_of_text((announcement_i+1)/(num_announcements+1), report)
                    print(f"[LLM]- Requesting single pass of announcement from _AUTOMATED_NEWS")
                    announcement_text = get_chatgpt_response(announcement_input_text, _AUTOMATED_NEWS(announcement_i, num_announcements))
                    # print(f"[LLM] - Requesting second pass of announcement from _AUTOMATED_NEWS")
                    # announcement_text = get_chatgpt_response(announcement_text, _AUTOMATED_NEWS())
                    announcement_text = re.sub(r'\*.*?\*', '', announcement_text)
                    announcement_text = announcement_text.replace("*", "")
                    queued_announcements.append(announcement_text)
                
                tts_queue_empty = False
                thread = threading.Thread(target=speak_tts_queue, args=([queued_announcements]))
                thread.start()

                for i in range(0, num_announcements):
                    announcement_text = queued_announcements[i]

                    if LOG_GENERATED_TEXT:
                        log_output = ""
                        log_output += f"[ANNOUNCEMENT] - {announcement_text}"
                        print(log_output.replace("\n","").replace("\r",""))

                    # action_text = get_chatgpt_response(announcement_text, _ACTION_TAKER())
                    # print("----------------------------------")
                    # print(f"[ACTION]\n{action_text}")
                    
                    # image_text = get_chatgpt_response(f"{scientist_text} {announcement_text}", _SYMBOLS_ONLY())
                    print(f"[LLM] - Requesting image description text from _IMAGE_DESCRIBER")
                    image_description_text = get_chatgpt_response(announcement_text, _IMAGE_DESCRIBER(), 300)
                    
                    if LOG_GENERATED_TEXT:
                        log_output = ""
                        log_output += f"[DESCRIPTION] - {image_description_text}"
                        print(log_output.replace("\n","").replace("\r",""))
                    
                    print(f"[LLM] - Requesting image text from _SYMBOLS_ONLY")
                    image_text = get_chatgpt_response(f"{image_description_text}", _SYMBOLS_ONLY(), 400)

                    num_images = 2
                    for image_i in range(0,num_images):
                        print(f"[DEBUG] - Generating image {image_i+1} of {num_images}")
                        flux.generate_image(flux_data, f"{_img_prompt_beginning} {image_text}")
                        # flux.generate_image(flux_data, f"{storyteller_text}")
                        
                        if LOG_GENERATED_TEXT:
                            log_output = ""
                            log_output += f"[IMAGE] - {_img_prompt_beginning} {image_text}"
                            print(log_output.replace("\n","").replace("\r",""))


