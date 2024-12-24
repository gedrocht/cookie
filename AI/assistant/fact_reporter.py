from utils import pick, roll
from config import _DEBUG_MODE, LOG_ROLLED_PROMPT_PARAMS, LOG_GENERATED_TEXT, _AI_OPTION_OPENAI, _AI_OPTION_GEMINI, _AI_OPTION_PAWANKRD, _AI_OPTION_GROQ, _AI_BEING_USED

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
