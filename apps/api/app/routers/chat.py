from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.jwt_utils import get_current_user

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatMessage(BaseModel):
    message: str


@router.post("/message")
def send_message(msg: ChatMessage, user=Depends(get_current_user)):
    return {
        "ok": True,
        "from": user.get("sub"),
        "echo": msg.message,
    }


@router.get("/history")
def get_history(user=Depends(get_current_user)):
    return {"ok": True, "from": user.get("sub"), "history": []}


@router.get("/conversations")
def get_conversations(user=Depends(get_current_user)):
    return {"ok": True, "from": user.get("sub"), "conversations": []}
