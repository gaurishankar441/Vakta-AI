from __future__ import annotations
import os, secrets, string, time
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt, redis
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, EmailStr

# Reuse centralized JWT config/helpers
from app.core.jwt_utils import JWT_SECRET, JWT_ALG, decode_jwt

router = APIRouter(prefix="/api/auth", tags=["auth-otp"])

# Config
JWT_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "60"))
OTP_TTL_SEC = int(os.getenv("OTP_TTL_SEC", "300"))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
OTP_DEV_RETURN_CODE = os.getenv("OTP_DEV_RETURN_CODE", "0") == "1"
OTP_RATE_MAX = int(os.getenv("OTP_RATE_MAX", "5"))          # requests
OTP_RATE_WINDOW = int(os.getenv("OTP_RATE_WINDOW", "600"))  # seconds

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    code: str

def _otp_key(email: str) -> str:
    return f"otp:{email.lower()}"

def _bl_key(jti: str) -> str:
    return f"jwt:blacklist:{jti}"

def _is_revoked(jti: str) -> bool:
    return bool(r.exists(_bl_key(jti)))

def _issue_jwt(sub: str) -> str:
    now = datetime.now(timezone.utc)
    jti = secrets.token_hex(8)
    payload = {
        "sub": sub,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXP_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

@router.post("/otp/request")
def otp_request(body: OTPRequest):
    # simple per-email rate limit
    rl_key = f"otp:rate:{body.email.lower()}"
    cnt = r.incr(rl_key)
    if cnt == 1:
        r.expire(rl_key, OTP_RATE_WINDOW)
    if cnt > OTP_RATE_MAX:
        raise HTTPException(status_code=429, detail="rate_limited")

    code = "".join(secrets.choice(string.digits) for _ in range(6))
    r.setex(_otp_key(body.email), OTP_TTL_SEC, code)

    resp = {"ok": True, "ttl_sec": OTP_TTL_SEC}
    if OTP_DEV_RETURN_CODE:
        resp["dev_code"] = code
    return resp

@router.post("/otp/verify")
def otp_verify(body: OTPVerify):
    val = r.get(_otp_key(body.email))
    if not val or val != body.code:
        raise HTTPException(status_code=400, detail="invalid_or_expired_code")

    # one-time code -> consume
    r.delete(_otp_key(body.email))
    token = _issue_jwt(body.email)
    return {"access_token": token, "token_type": "bearer", "expires_in": JWT_EXP_MIN * 60}

@router.get("/me")
def me(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing_token")
    token = authorization.split(" ", 1)[1]
    payload = decode_jwt(token)

    jti = payload.get("jti")
    if jti and _is_revoked(jti):
        raise HTTPException(status_code=401, detail="token_revoked")
    return {"sub": payload.get("sub"), "exp": payload.get("exp")}

@router.post("/refresh")
def refresh(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing_token")

    old = authorization.split(" ", 1)[1]
    try:
        # allow refresh even if exp passed; we only need sub/jti
        payload = jwt.decode(old, JWT_SECRET, algorithms=[JWT_ALG], options={"verify_exp": False})
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid_token")

    jti = payload.get("jti")
    if jti and _is_revoked(jti):
        raise HTTPException(status_code=401, detail="token_revoked")

    sub = payload.get("sub")
    return {"access_token": _issue_jwt(sub), "token_type": "bearer", "expires_in": JWT_EXP_MIN * 60}

@router.post("/logout")
def logout(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing_token")
    token = authorization.split(" ", 1)[1]
    payload = decode_jwt(token)

    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        raise HTTPException(status_code=400, detail="token_missing_jti_or_exp")

    ttl = max(0, int(exp - time.time()))
    if ttl <= 0:
        return {"ok": True, "already_expired": True}

    r.setex(_bl_key(jti), ttl, "1")
    return {"ok": True, "revoked_for_sec": ttl}
