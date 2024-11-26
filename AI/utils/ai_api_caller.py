import os
from groq import Groq
from random import choice
import sys

sys.path.append('../')
from utils import util
from utils import groq_api

groq_api_key = os.environ.get("GROQ_API_KEY")
groq_url = "https://api.groq.com/openai/v1/models"

'''
with open("./groqcloud.txt", "r") as file:
    api_key = file.read().strip()
'''

groq_client = Groq(
    api_key=groq_api.get_api_key(),
)
def log(msg):
  util.log(msg, "AICALL")

def use_groq(query="", prompt="you are a helpful assistant", model="llama3-8b-8192"):
    log(f"Model: {model}")
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
        model=model
    )
    output = chat_completion.choices[0].message.content
    return output

AI_MODELS = { 
    "great": [ 
        "llama3-70b-8192", 
        "llama-3.2-90b-text-preview", 
        "llama3-groq-70b-8192-tool-use-preview"
    ],
    "good": [ 
        "llama-3.1-70b-versatile", 
        "llama-3.2-11b-text-preview", 
        "llama3-8b-8192",
    ],
    "okay": [ 
        "llama3-groq-8b-8192-tool-use-preview", 
        "llama-3.2-3b-preview", 
        "llama-3.2-1b-preview", 
        "gemma-7b-it"
    ]
}

def get_great_model():
    return choice(AI_MODELS["great"])

def get_good_model():
    return choice(AI_MODELS["good"])

def get_okay_model():
    return choice(AI_MODELS["okay"])