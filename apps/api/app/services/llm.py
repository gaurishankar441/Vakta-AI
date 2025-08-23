import os
from typing import Optional

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # if not installed at build time

_client = None

def _get_client() -> Optional["OpenAI"]:
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None
    _client = OpenAI(api_key=api_key)
    return _client

def complete(prompt: str) -> Optional[str]:
    client = _get_client()
    if not client:
        return None
    try:
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role":"system","content":"You are Priya, a friendly Indian English coach. Reply in Hinglish, concise, encouraging."},
                {"role":"user","content":prompt},
            ],
            temperature=0.6,
            max_tokens=220,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print("LLM error:", e)
        return None
