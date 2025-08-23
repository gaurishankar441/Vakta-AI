from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.db import get_db
from app.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.models import User

router = APIRouter()

class SignupIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(body: SignupIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    u = User(email=body.email, hashed_password=get_password_hash(body.password))
    db.add(u); db.commit(); db.refresh(u)
    return {"id": str(u.id), "email": u.email}

@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == body.email).first()
    if not u or not verify_password(body.password, u.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(u.id))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(current = Depends(get_current_user)):
    return {"id": str(current.id), "email": current.email}
