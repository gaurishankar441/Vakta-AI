from typing import Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings

_client: Optional[OpenAI] = None
def _client_once():
    global _client
    if _client is None: _client = OpenAI()
    return _client

class OpenAILLM:
    def name(self): return "openai"
    async def complete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text", "")
        client = _client_once()
        model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
        try:
            r = client.responses.create(model=model, input=f"User said: {text}\nRespond concisely as a role-play coach.")
            out = (r.output_text or "").strip()
        except Exception:
            out = f"I heard: {text}"
        return {
            "text": out,
            "citations": [
                {"id":"doc1","title":"Coaching Guide","url":"https://example.com/guide"},
                {"id":"doc2","title":"Role-play Tips","url":"https://example.com/tips"},
            ]
        }
