from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import json

from chat_schemas import PromptData

app = FastAPI()

# If you want to restrict origins in production, replace "*" with the specific domain(s)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],            # or list of methods, e.g. ["GET", "POST"]
    allow_headers=["*"]             # or list of allowed headers
)

# Pydantic model matching the desired JSON structure
class JsonData(BaseModel):
    name: str
    prompt: PromptData
    voice: str

# Directory to store and read JSON files
DATA_DIR = "data"

# Ensure the directory exists at startup
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.get("/")
def root():
    return {"message": "JSON read/write API is running!"}

@app.get("/read-json/{filename}")
def read_json(filename: str):
    """
    Read a JSON file from the data directory.
    Expected file extension: .json
    """
    file_path = os.path.join(DATA_DIR, f"{filename}.json")
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Read and return the JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data

@app.post("/write-json/{filename}")
def write_json(filename: str, json_data: JsonData):
    """
    Write (create/update) a JSON file in the data directory.
    Expected file extension: .json
    Request body must match the JsonData schema.
    """
    file_path = os.path.join(DATA_DIR, f"{filename}.json")
    
    # Convert the JsonData (Pydantic model) to a Python dict
    data_dict = json_data.dict()
    
    # Write the dict to a JSON file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2, ensure_ascii=False)
    
    return {"message": f"File '{filename}.json' written successfully.", "data": data_dict}

@app.delete("/delete-json/{filename}")
def delete_json(filename: str):
    """
    Delete a JSON file from the data directory.
    """
    file_path = os.path.join(DATA_DIR, f"{filename}.json")
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    os.remove(file_path)
    return {"message": f"File '{filename}.json' deleted successfully."}
