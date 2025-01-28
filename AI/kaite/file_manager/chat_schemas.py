# file_manager/chat_schemas.py
from pydantic import BaseModel
from typing import List, Optional

class MessageData(BaseModel):
    source: str
    message: str

class PromptData(BaseModel):
    core: str
    flux: str
    memories: str