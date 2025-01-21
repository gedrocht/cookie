import json

class AIComm:
    """
    A simple class holding data for 'query' and 'prompt'
    """
    def __init__(self, query: str, prompt: str):
        self.query = query
        self.prompt = prompt

def load_ai_comm_from_json(json_file_path: str) -> AIComm:
    """
    Loads JSON data from the given file path and returns an AIComm instance.
    Expects the JSON file to have keys: 'query', 'prompt'.
    """
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
    # Create and return the AIComm instance from JSON data
    return AIComm(
        query=data.get('query', ''),
        prompt=data.get('prompt', '')
    )
