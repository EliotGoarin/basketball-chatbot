## `backend/models/schemas.py`
from pydantic import BaseModel, Field
from typing import List, Optional

class ChatTurn(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatTurn]
    top_k: Optional[int] = 4

    def last_user_message(self) -> str:
        for m in reversed(self.messages):
            if m.role == "user":
                return m.content
        return ""

class ChatResponse(BaseModel):
    answer: str
    retrieved: List[str]
