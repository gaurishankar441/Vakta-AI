from uuid import UUID as UUID_t
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.message import Message
from app.models.conversation import Conversation

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# ---- Schemas ----
class ConversationCreate(BaseModel):
    title: Optional[str] = None

class SendMessage(BaseModel):
    message: str
    conversation_id: Optional[UUID_t] = None

# ---- Helpers ----
def _get_or_create_conversation(db: Session, user: User, conv_id: Optional[UUID_t]) -> Conversation:
    if conv_id:
        convo = db.query(Conversation).filter(
            Conversation.id == conv_id,
            Conversation.user_id == user.id
        ).first()
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return convo

    convo = (db.query(Conversation)
             .filter(Conversation.user_id == user.id)
             .order_by(Conversation.created_at.desc())
             .first())
    if convo:
        return convo

    convo = Conversation(user_id=user.id, title="Default")
    db.add(convo); db.commit(); db.refresh(convo)
    return convo

# ---- Conversations ----
@router.post("/conversations")
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    convo = Conversation(user_id=user.id, title=(payload.title or "Untitled"))
    db.add(convo); db.commit(); db.refresh(convo)
    return {"id": str(convo.id), "title": convo.title, "created_at": convo.created_at.isoformat()}

@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    convos = (db.query(Conversation)
              .filter(Conversation.user_id == user.id)
              .order_by(Conversation.created_at.desc())
              .all())
    return [{"id": str(c.id), "title": c.title, "created_at": c.created_at.isoformat()} for c in convos]

# ---- Chat: send ----
@router.post("/message")
def send_message(
    payload: SendMessage,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Ensure conversation exists or create
    convo = _get_or_create_conversation(db, user, payload.conversation_id)

    # User message
    um = Message(
        user_id=user.id,
        role="user",
        content=payload.message,
        conversation_id=convo.id,
    )
    db.add(um)

    # Assistant echo response
    echo = f"echo: {payload.message}"
    am = Message(
        user_id=user.id,
        role="assistant",
        content=echo,
        conversation_id=convo.id,
    )
    db.add(am)

    # Commit + refresh both
    db.commit()
    db.refresh(um)
    db.refresh(am)

    # Structured response
    return {
        "conversation_id": str(convo.id),
        "user_message": {
            "id": str(um.id),
            "role": um.role,
            "content": um.content,
            "created_at": um.created_at.isoformat(),
        },
        "assistant_message": {
            "id": str(am.id),
            "role": am.role,
            "content": am.content,
            "created_at": am.created_at.isoformat(),
        },
    }


# ---- Chat: history ----
@router.get("/history")
def history(
    conversation_id: Optional[UUID_t] = Query(None),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    convo = _get_or_create_conversation(db, user, conversation_id)
    msgs: List[Message] = (
        db.query(Message)
        .filter(Message.user_id == user.id, Message.conversation_id == convo.id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in msgs
    ]
