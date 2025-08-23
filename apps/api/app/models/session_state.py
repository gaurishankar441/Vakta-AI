from dataclasses import dataclass
@dataclass
class SessionState:
    user_id: str|None = None
    context: str = ""
