from typing import Optional, Tuple
from jose import jwt, JWTError
import os
from app.core.config import settings
try:
    # optional: use same secret/algorithm as login uses
    from ..core import security as sec
except Exception:
    sec = None

def extract_token_from_ws(ws) -> Optional[str]:
    tok = ws.query_params.get("token")
    if tok:
        return tok
    try:
        auth = ws.headers.get("authorization") or ws.headers.get(b"authorization")
        if auth:
            if isinstance(auth, bytes):
                auth = auth.decode()
            parts = auth.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                return parts[1]
    except Exception:
        pass
    return None

def _candidates():
    alg = "HS256"
    c = []
    if getattr(settings, "JWT_SECRET", None):
        c.append((settings.JWT_SECRET, [alg]))
    if sec and getattr(sec, "SECRET_KEY", None):
        a = getattr(sec, "ALGORITHM", alg)
        c.append((sec.SECRET_KEY, [a]))
    env = os.getenv("SECRET_KEY")
    if env:
        a = getattr(sec, "ALGORITHM", alg) if sec else alg
        c.append((env, [alg, a]))
    # de-dup keys while preserving order
    seen = set(); out=[]
    for k, al in c:
        if k and k not in seen:
            seen.add(k); out.append((k, list(dict.fromkeys(al))))
    return out or [(getattr(settings,"JWT_SECRET","changeme"), [alg])]

def verify_token(token: str) -> Tuple[bool, Optional[str]]:
    for key, algs in _candidates():
        try:
            payload = jwt.decode(token, key, algorithms=algs)
            sub = payload.get("sub") or payload.get("user_id") or payload.get("uid")
            return True, sub
        except JWTError:
            continue
    return False, None
