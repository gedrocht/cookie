import gpt
from time import sleep

_MEMORY_MANAGER_PROMPT = \
'''You are in charge of managing a short list of contextual facts to keep track of during a session with another GPT. \
You will look at queries sent from the user to the other GPT and evaluate how the list of contextual facts should change based on that. \
You will use your best judgment, evaluating the new query alongside the already existing contextual in order to output a new list of memories. \
Based on logical assessment of the available information, the new list might have had memories removed, added, and/or summarized. \
You will use your best judgment to decide if the list of facts to remember will even be changed at all. \
Your only output will be the new list of memories and nothing else. You must only say \"context:\" followed by the latest list of remembered facts.'''

def init():
  return "None"

def eval(memories, query):
  response = gpt.get_chatgpt_response(f"context: {memories} / User query to other GPT: {query}", _MEMORY_MANAGER_PROMPT)
  while response.find("context:") == -1 and response.find("User query to other GPT") == -1:
    print(f"[MEM] response was: [{response}]. Retrying...")
    sleep(1)
  response = gpt.get_chatgpt_response(f"context: {memories} / User query to other GPT: {query}", _MEMORY_MANAGER_PROMPT)
  new_memories = response.split(":")[1:][0].strip()
  print(f"[MEM] memories:\n{new_memories}")
  return new_memories

if __name__ == "__main__":
  memories = "None"