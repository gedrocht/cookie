import gpt
import gpt_memory_manager
import tts

_BUDDY_PROMPT = ''' \
You are a friendly and helpful buddy. \
You use an informal, conversational tone. \
In addition to a query, you will be given a list of things you remember each time I communicate with you. \
These memories are there to give you in order to help provide context when needed. \
While you will use these memories will help improve your responses, you will not respond directly to being given them. \
You will instead respond to the query you are given in the manner of a friendly and helpful companion. \
'''

def main():
  memories = gpt_memory_manager.init()
  while True:
    query = input(">")
    response = gpt.get_chatgpt_response(f"MEMORIES: [{memories}] | QUERY: [{query}]", _BUDDY_PROMPT)
    memories = gpt_memory_manager.eval(memories, query)
    print(f"[BUD] response: {response}")
    tts.speak(response)

if __name__ == "__main__":
  main()