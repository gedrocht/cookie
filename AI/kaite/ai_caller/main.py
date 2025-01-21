import sys
sys.path.append('../../../')
from AI.brigade import aidoer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Define a Pydantic model for request body validation
class DoRequest(BaseModel):
    query: str
    prompt: str

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

@app.get("/")
def root():
    return {"message": "API for executing do() is running."}

@app.post("/do")
def execute_do(payload: DoRequest):
    """
    Executes the 'do' function with the given query and prompt.
    Returns the result as JSON.
    """
    result = aidoer.do(payload.query, payload.prompt)
    return {"result": result}

