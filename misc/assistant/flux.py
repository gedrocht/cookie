import json
from urllib import request, parse
import random

# Function to queue the prompt to the ComfyUI API
def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = request.Request("http://192.168.0.164:8188/prompt", data=data)
    response = request.urlopen(req)
    print(f"Response: {response.read()}")

# Function to load the JSON workflow from a file
def load_json_from_file(filepath):
    try:
        with open(filepath, 'r') as file:
            prompt = json.load(file)
            return prompt
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def init():
  # Set the path to your JSON workflow file
  workflow_file = 'workflow_api.json'
  # Load the JSON workflow
  json = load_json_from_file(workflow_file)
  return json

def generate_image(json, prompt):
    # Set the text prompt for our positive CLIPTextEncode (Key: 6)
    json["6"]["inputs"]["text"] = prompt

    # Set the seed for our KSampler node (Key: 31)
    json["31"]["inputs"]["seed"] = 5

    # Queue the prompt to the API
    queue_prompt(json)