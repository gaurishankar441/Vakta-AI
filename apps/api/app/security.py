import os, uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .db import get_db
from .models import User

SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXP_MIN", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_password_hash(pw: str) -> str: return pwd_context.hash(pw)
def verify_password(pw: str, hashed: str) -> bool: return pwd_context.verify(pw, hashed)
def create_access_token(sub: str, minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": sub, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
                             headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: Optional[str] = payload.get("sub")
        if sub is None: raise cred_exc
    except JWTError:
        raise cred_exc
    try:
        user_id = uuid.UUID(sub)
    except Exception:
        raise cred_exc
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise cred_exc
    return user
