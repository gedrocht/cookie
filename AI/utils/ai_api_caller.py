import os
from groq import Groq
from random import choice
import sys

sys.path.append('../')
from utils import util
from utils import groq_api

from colorama import Fore, Style, init

groq_api_key = os.environ.get("GROQ_API_KEY")
groq_url = "https://api.groq.com/openai/v1/models"

'''
with open("./groqcloud.txt", "r") as file:
    api_key = file.read().strip()
'''

_VERBOSE = False

groq_client = Groq(
    api_key=groq_api.get_api_key(),
)
def log(msg, color=Fore.WHITE):
  util.log(msg, "AICALL", color)

def use_api_fallback(query="", prompt="", priority="great"):
    """
    Attempt to use models from a specified priority group ("great", "good", "okay").
    Randomly select models from the group and retry until all models are exhausted.
    """
    if priority not in AI_MODELS:
        log(f"Invalid priority group: {priority}", Fore.RED)
        raise RuntimeError(f"Invalid priority group: {priority}")

    # Get a list of models in the priority group
    models = AI_MODELS[priority][:]
    tried_models = []
    log(f"Choosing from {priority} models.")

    while models:
        model = choice(models)
        log(f"Model chosen: {model}")
        try:
            if _VERBOSE:
                log(f"Trying model: {model}")
            return use_groq(query, prompt, model)
        except Exception as e:
            log(f"Model {model} failed with error: {str(e)}", Fore.RED)
            # Move the failed model to the tried list
            log(f"Retrying with new model.")
            tried_models.append(model)
            models.remove(model)

    # If all models in the group fail, table flip!
    log(f"All models in the '{priority}' group failed. Tried models: {tried_models}", Fore.RED)
    raise RuntimeError(f"(╯°□°）╯︵ ┻━┻ All models in '{priority}' failed.")

def get_model_group(model):
    """
    Identify the quality group ('great', 'good', or 'okay') for the given model.
    Returns the group name if found, otherwise returns None.
    """
    for group, models in AI_MODELS.items():
        if model in models:
            return group
    return None

def is_great_model(model):
    """
    Check if the given model belongs to the 'great' group.
    """
    return get_model_group(model) == "great"

def is_good_model(model):
    """
    Check if the given model belongs to the 'good' group.
    """
    return get_model_group(model) == "good"

def is_okay_model(model):
    """
    Check if the given model belongs to the 'okay' group.
    """
    return get_model_group(model) == "okay"

# Wrappers for specific groups
def use_api_great(query="", prompt=""):
    return use_api_fallback(query, prompt, "great")

def use_api_good(query="", prompt=""):
    return use_api_fallback(query, prompt, "good")

def use_api_okay(query="", prompt=""):
    return use_api_fallback(query, prompt, "okay")

def use_groq(query="", prompt="you are a helpful assistant", model="llama3-8b-8192"):
    if _VERBOSE:
        log(f"Model: {model.strip()}")
        log(f"Query: {query.strip()}")
        log(f"Prompt: {prompt.strip()}")

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
    if _VERBOSE:
        log(f"Result: {output.strip()}")
    return output

AI_MODELS = {
    "great": [
#        "llama-3.2-90b-text-preview",
        "llama-3.2-90b-vision-preview",
        "llama3-70b-8192",
#        "llama3-groq-70b-8192-tool-use-preview",
        "llama-3.3-70b-specdec",
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile"
    ],
    "good": [
        "gemma2-9b-it",
        "llama-3.2-11b-text-preview",
        "llama-3.2-11b-vision-preview",
        "llama3-8b-8192",
        "llama3-groq-8b-8192-tool-use-preview",
        "llama-3.1-8b-instant",
        "llama-guard-3-8b",
        "llava-v1.5-7b-4096-preview",
        "mixtral-8x7b-32768"
    ],
    "okay": [
        "gemma-7b-it",
        "llama-3.2-3b-preview",
        "llama-3.2-1b-preview"
    ]
}

def get_great_model():
    return choice(AI_MODELS["great"])

def get_good_model():
    return choice(AI_MODELS["good"])

def get_okay_model():
    return choice(AI_MODELS["okay"])