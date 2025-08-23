from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.models.conversation import Conversation
from app.models.user import User
from app.routers.auth import get_current_user  # your existing dependency

router = APIRouter()  # no prefix; we'll mount with /api/v1/chat in main.py

class ConversationCreate(BaseModel):
    title: str | None = None

@router.post("/conversations")
def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    convo = Conversation(user_id=user.id, title=payload.title or "Untitled")
    db.add(convo); db.commit(); db.refresh(convo)
    return {"id": str(convo.id), "title": convo.title, "created_at": convo.created_at.isoformat()}

@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    convos = (db.query(Conversation)
                .filter(Conversation.user_id == user.id)
                .order_by(Conversation.created_at.desc())
                .all())
    return [{"id": str(c.id), "title": c.title, "created_at": c.created_at.isoformat()} for c in convos]
