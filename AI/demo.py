import os
import openai
from openai import OpenAI

# client = OpenAI()
'''
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Pretend that you are Jarvis from Iron Man / The Avengers, here to help me out.",
        }
    ],
    model="gpt-3.5-turbo",
)
'''  
client = OpenAI()

def chat_with_ai(initial_message):
    messages = [{"role": "user", "content": initial_message}]
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            print("Exiting the conversation.")
            break

        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",  # Replace with the model you're using
        )


        ai_message = response.choices[0].message.content
        print(f"AI: {ai_message}")

        # Append the AI's response to the conversation history
        messages.append({"role": "assistant", "content": ai_message})
        # messages.append({"role": "user", "content": ai_message})

# Start the conversation with an initial message
chat_with_ai("Pretend that you are Jarvis from Iron Man / The Avengers, here to help me out.")