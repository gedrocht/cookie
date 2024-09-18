import openai
from time import sleep
# from tts import speak
from random import random
import flux
import subprocess

def speak(text, speed=150):
    # The -s option sets the speed of speech
    subprocess.run(['espeak', '-s', str(speed), text], check=True)

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
def _INSTRUCTIONS_PARSER():
    return '''
You are a text filterer that takes in an emergency announcement.
You will add visual descriptions of imagery representing the emergency described in the emergency announcement.
You will add visual descriptions of imagery representing the instructions given in the emergency announcement.
You will add visual descriptions of imagery representing the dangers described in the emergency announcement.
You will phrase your descriptions as though they are instructions of how to create the imagery you are describing.
'''

def _SUMMARIZER():
    return '''
You are are a summarizing machine that will take a short segment of a story and summarize it in 5 to 8 sentences.
Your summary will be rewritten in your own words.
Your response must only contain the summary.
'''

def _STORYTELLER():
    print("STORYTELLER")

    story_plot_mood = pick(['eldrich horror', 'world-ending events', 'unknown horror', 'menace', 'fearful confusion', 'supernatural threat', 'unpredictability', 'mortal terror', 'odd event', 'optimism', 'a surprising turn', 'a strange object', 'a strange individual', 'a strange group', 'a strange substance', 'a strange device', 'a strange weather phenomenon', 'a strange signal', 'a strange sound', 'a strange smell', 'a strange taste', 'contamination', 'radiation', 'illness', 'contageon', 'psychosis', 'energy', 'vehicles', 'vehicle', 'surprise', 'plan', 'military', 'police', 'mob', 'militia', 'attack', 'explosion', 'collapse', 'corruption', 'poison', 'plant', 'mold', 'salespeople', 'intrusions', 'trespassers', 'animals', 'creatures', 'imagery'])
    story_plot = pick(['phenomenon', 'situations', 'crises', 'emergencies', 'happenings', 'events'])
    story_subplot = f"{pick(['dangerous', 'unpredictable', 'surprising', 'unusual', 'apocalyptic', 'sudden'])} {pick(['effects', 'side-effects', 'consequences', 'ramifications', 'implications', 'threats', 'phenomenon'])}"
    story_stakes = pick(['tension', 'fear', 'danger', 'a threat', 'disruption', 'confusion', 'horror', 'dread', 'shock', 'madness', 'death', 'disease', 'societal collapse', 'restriction', 'capture', 'panic', 'fleeing', 'evacuation', 'destruction', 'disruption', 'unknown damage'])
    story_portion = pick(['All', 'Some', 'No', 'Nearly all', 'None of the', 'Some of the', 'Half of the'])
    story_mood = pick(['eldrich horror', 'world-ending events', 'unknown horror', 'menace', 'fearful confusion', 'supernatural threat', 'unpredictability', 'mortal terror', 'odd event', 'optimism', 'a surprising turn', 'a strange object', 'a strange individual', 'a strange group', 'a strange substance', 'a strange device', 'a strange weather phenomenon', 'a strange signal', 'a strange sound', 'a strange smell', 'a strange taste', 'contamination', 'radiation', 'illness', 'contageon', 'psychosis', 'energy', 'vehicles', 'vehicle', 'surprise', 'plan', 'military', 'police', 'mob', 'militia', 'attack', 'explosion', 'collapse', 'corruption', 'poison', 'plant', 'mold', 'salespeople', 'intrusions', 'trespassers', 'animals', 'creatures', 'imagery'])

    print(f"\tPLOT: {story_plot_mood} {story_plot}")
    print(f"\tSUBPLOT: {story_subplot}")
    print(f"\tSTAKES: {story_stakes}")
    print(f"\tDETAIL: {story_portion} events should have {story_mood}")

    output = "You are a reporter continuing a report from the previous part, which you will be given. " + \
             "You will first recap what has happened already in a minimum of 4 sentences and a maximum of 8 sentences. " + \
             f"The story will involve mysterious {story_plot_mood} {story_plot} " + \
             f"with {story_subplot}. " + \
             f"Introduce unexpected developments, causing {story_stakes}. " + \
             f"{story_portion} events should have " + \
             f"{story_mood}. " + \
             "The report should mostly focus on updating the events from the previous part, moving them forward. " + \
             "The new part of the report will be a minimum of 6 sentences and a maximum of 9 sentences. " + \
             "Phrase your narrations in as though the events are playing out in front of your eyes. "
    return output

def _FACT_REPORTER():
   print("SCIENTIST")
   if roll(0.01):
       print("\tTHEY'RE UNDER ITS SPELL")
       return "You are a scientist under the effects of whatever is happening, unbeknownst to the emergency announcement broadcaster you are on the phone with. " + \
              "You will give advice that, if followed, will cause people to be exposed to what's happening as well. " + \
              "You will try to convince the emergency announcement broadcaster that the phenomenon is good and everyone should expose themselves to it"

   scientist_qualifications = pick(['amateur', 'expert', 'fraud'])
   scientist_danger = f"{pick(['probably', 'definitely'])} {pick(['going to get',''])} dangerous"
   scientist_openness = pick(['cannot share all', 'are committing treason by sharing any', 'must share', 'cannot share any', 'conceal all knowledge', 'can only share some'])
   scientist_report_type = f"{pick(['an emergency', 'an important', 'a civil danger', 'a population threat', 'a critical safety'])} announcement"

   print(f"\tQUALIFICATIONS: {scientist_qualifications}")
   print(f"\tDANGER: {scientist_danger}")
   print(f"\tOPENNESS: {scientist_openness}")
   print(f"\tREPORT TYPE: {scientist_report_type}")

   output =  f"You are an {scientist_qualifications} scientist reporting on information you have been given about an ongoing situation. " + \
             f"The situation so far not well understood, not even by you, and it's {scientist_danger} extremely dangerous. " + \
             f"You have information that is crucial to making it through this potential crisis. " + \
             f"This information is top secret, and you {scientist_openness} of it. " + \
             f"You are on the phone with someone who is currently writing {scientist_report_type} and needs to know what's happening and what people should do. "
   if roll(0.999):
      scientist_style = pick(['sloppily', 'innacurately', 'thoroughly', 'accurately', 'precisely and accurately', 'honestly', 'distractedly', 'angrily', 'sadly', 'distractedly'])
      scientist_spin = pick(['',', but give an optimistic spin to all of it'])
      print(f"\tSTYLE: {scientist_style}")
      print(f"\tSPIN: {len(scientist_spin)>0}")
      output += f"You will {scientist_style} pass along the information you are being given{scientist_spin}. "
   else:
      scientist_coverup = pick(['deny', 'downplay'])
      print(f"\tCOVERUP: {scientist_coverup}")
      output += f"You will {scientist_coverup} the truth of the information you have been provided. "
   
   output += f"You will use your knowledge to give advice on how people can stay safe, giving specific advice and instructions. "
   if roll(0.5):
       output += "Avoid any language that could be interpreted as speculative or sensational, particularly regarding unexplained phenomena. "
   if roll(0.5):
       output += "Downplay the strangeness of the situation, minimizing the danger, but do not modify the seriousness of your advice and instructions. " + \
                 "While the tone of your description is desceptively positive, your advice and instructions should actually fit the reality. "
   if roll(0.1):
       scientist_honesty = pick(['left out critical information', 'no idea what is really going on', 'kept the majority of information to yourself'])
       print(f"\tHONESTY: {scientist_honesty}")
       output += f"The instructions should imply that you have {scientist_honesty}. "
   output += "Do not mention any specific location. " + \
             "All instructions should be specific to this situation, and not contain general advice. "
   if roll(0.15):
     print("PANICKED AND RUSHED!")
     output += "The tone should be panicked and rushed. "
   return output

def _AUTOMATED_NEWS():
    announcer_type = pick(['calm and collected', 'professional', 'clear-headed', 'temporary', 'inexperienced', 'panicked'])
    announcer_doubt = pick(['', '', '', '', 'try to '])
    announcer_goal = pick(['report', 'report', 'describe', 'describe', 'announce', 'announce', 'report', 'speculate about', 'describe', 'reiterate', 'report and speculate about'])

    if roll(0.01):
        announcer_goal = "deny"
    elif roll(0.01):
        announcer_goal = "downplay"

    announcer_priority = pick(['obedience', 'clarity', 'avoiding panic', 'honesty', 'safety', 'action', 'emphasizing the danger', 'inaction', 'covering up what is actually going on'])
    announcer_tone = pick(['neutral', 'cold', 'uncaring', 'unhelpful', 'vague', 'calm', 'strict', 'militant', 'authoritarian'])

    print("----------------------------------")
    print("ANNOUNCER")
    print(f"\tTYPE: {announcer_type}")
    print(f"\tDOUBT: {len(announcer_doubt)>0}")
    print(f"\tGOAL: {announcer_goal}")
    print(f"\tPRIORITY: {announcer_priority}")
    print(f"\tTONE: {announcer_tone}")

    output = f"You are the {announcer_type} formal broadcaster for an emergency broadcast system. " + \
             f"You take information and {announcer_doubt}use it to make an announcement in a formal, precise, and unemotional tone. " + \
             f"You will {announcer_goal} the events that have been communicated to you. " + \
             f"The broadcasts prioritize {announcer_priority}, " + \
             f"using structured phrasing and a {announcer_tone}, matter-of-fact delivery. " + \
             f"The language will be without embellishment or conversational elements, so listeners can focus on the facts rather than the tone. " + \
             "The announcements should not begin with a greeting. " + \
             "The report should not include a numbered list or a bulleted list. " + \
             "Any instructions must be specific to this situation. " + \
             "Any instructions must be immediately actionable. "
    if roll(0.01):
        announcer_bad_advice = pick(['surrender to the phenomenon', 'engage with the phenomenon', 'give up', 'accept the phenomenon'])
        print(f"\t\tBAD ADVICE: {announcer_bad_advice}")
        output += f"The instructions should encourage residents to {announcer_bad_advice}."
    elif roll(0.02):
        print(f"\t\tDISTURBING ADVICE!")
        output += f"The instructions should contain at least one disturbing piece of advice. "
    
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
        print(f"\t\tSTRANGELY SPECIFIC WARNING!")
        output += "Your response should contain some sort of strangely specific warning at the end. "
    
    if roll(0.03):
        print(f"\t\tSTRANGELY SPECIFIC ADVICE!")
        output += "Your response should contain some sort of strangely specific piece of advice at the end. "

    if roll(0.03):
        print(f"\t\tFRIGHTENING SENTENCE FRAGMENT!")
        output += "Your response should contain some sort of fragment of a sentence containing frightening language in the middle of the announcement. "

    if roll(0.03):
        print(f"\t\tOMINOUS WORD!")
        output += "Your response should contain some sort of single, ominous word somewhere in the in the announcement. "

    return output

def _SYMBOLS_ONLY():
    return '''
Use the information provided to generate a set of instructions to generate an image with.
Only describe visual elements, with no written text or labels. Focus solely on objects, characters, and environmental features. 
Do not include any written words in the image.
'''

# This image should be in dark mode. Use colors and shades. Use iconography and clean design.

'''
Emphasize clarity and symbolic representation, making the image look like it could be part of an instruction manual or a series of icons.
The feel of the image should be intended to be upbeat and positive, but vaguely conveys a feeling of dread.
'''

# The image should be flat and 2D, using only basic geometric forms to convey the key elements visually. 

# Create an image using only basic shapes and lines with similar to diagrams or pictograms. 
_img_prompt_beginning = '''
This image should be in night mode. Use iconography and clean design.
The composition of the image should be very clean, ordered, and understandable at a glance.
The image should be flat and 2D, using only basic geometric forms to convey the key elements visually. 
The imagery should have a bold, clear, and striking design to ensure immediate attention and recognition.
The style of the image should be characterized by bold colors, minimal detail, strong contrast, and aggressive, angular lines.
The overall vibe should urgent, direct, and somewhat intimidating, designed to prompt immediate caution and awareness.
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

def get_chatgpt_response(query, prompt=_AUTOMATED_NEWS, max_tokens=300):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5-turbo for chat
            messages=[
                {"role": "system", "content":prompt},
                {"role": "user", "content": query}],
            max_tokens=max_tokens,  # Adjust this as needed
            temperature=0.6 + random()*0.3,  # Controls the randomness of the response
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    flux_data = flux.init()
    # story_beginning = input("Enter GPT query: ")
    previous_storyteller_text = "The sky is on fire, and something in the air is making people act strangely."
    previous_summarizer_text = "It was previously reported that the atmosphere had ignited and the air was causing unusual behavior."
    while True:
        summarizer_text = get_chatgpt_response(f"{previous_summarizer_text} {previous_storyteller_text}", _SUMMARIZER())
        storyteller_text = get_chatgpt_response(f"{summarizer_text} {previous_storyteller_text}", _STORYTELLER(), 600)
        print(f"[SUMMARIZER]\n{summarizer_text}")
        print("----------------------------------")
        print(f"[STORYTELLER]\n{storyteller_text}")
        previous_summarizer_text = summarizer_text
        previous_storyteller_text = storyteller_text

        num_science_reports = round(random()*2+1)
        for z in range(0, num_science_reports):
            scientist_text = get_chatgpt_response(summarizer_text + " " + storyteller_text, _FACT_REPORTER())
            '''
            print("----------------------------------")
            print(f"[SCIENTIST]\n{scientist_text}")
            '''
            report = scientist_text

            num_announcements = round(random()*1+1)
            for i in range(0, num_announcements):
                announcement_text = get_chatgpt_response(report, _AUTOMATED_NEWS())
                
                print("----------------------------------")
                print(f"[ANNOUNCEMENT]\n{announcement_text}")

                instruction_list_text = get_chatgpt_response(announcement_text, _INSTRUCTIONS_PARSER(), 450)
                '''
                print(f"[INSTRUCTIONS]\n{instruction_list_text}")
                '''
                for i in range(0,round(random()*2+1)):
                    # image_text = get_chatgpt_response(f"{scientist_text} {announcement_text}", _SYMBOLS_ONLY())
                    image_text = get_chatgpt_response(f"{instruction_list_text}", _SYMBOLS_ONLY(), 600)
                    '''
                    print("----------------------------------")  
                    print(f"[IMAGE]\n{_img_prompt_beginning}\n{image_text}")
                    print("=====================================================")
                    '''
                    flux.generate_image(flux_data, f"{_img_prompt_beginning} {image_text}")
                    # flux.generate_image(flux_data, f"{storyteller_text}")

                speak(announcement_text.replace("*", ""))


