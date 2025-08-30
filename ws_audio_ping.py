#!/usr/bin/env python3
import argparse, asyncio, json, pathlib, os, websockets

from contextlib import asynccontextmanager

# -- version-adaptive websockets connect (11.x extra_headers vs 15.x headers) --
@asynccontextmanager
async def ws_connect_compat(url, headers=None):
    import websockets
    try:
        # websockets 11–12
        async with websockets.connect(url, extra_headers=headers, max_size=None) as _ws:
            yield _ws
    except TypeError:
        # websockets 15+
        async with websockets.connect(url, headers=headers, max_size=None) as _ws:
            yield _ws

def read_token(token_file: str | None) -> str:
    if os.getenv("TOK"):
        return os.environ["TOK"].strip()
    p = pathlib.Path(token_file or ".auth_token")
    return p.read_text().strip()

async def wait_ready(ws):
    while True:
        raw = await ws.recv()
        try:
            msg = json.loads(raw)
        except Exception:
            continue
        if isinstance(msg, dict) and msg.get("type") == "ready":
            return

async def run(url: str, token: str, use_query: bool):
    if use_query:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}token={token}"
        headers = {}
    else:
        headers = {"Authorization": f"Bearer {token}"}

    async with ws_connect_compat(url, headers=headers) as ws:
        await wait_ready(ws)
        await ws.send(json.dumps({"type": "echo", "text": "ping"}))
        while True:
            raw = await ws.recv()
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            if msg.get("type") == "echo":
                text = msg.get("text", "")
                try:
                    inner = json.loads(text) if isinstance(text, str) and text.startswith("{") else {"type":"echo","text":text}
                except Exception:
                    inner = {"type":"echo","text":text}
                print("echo:", inner.get("text"))
                return

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="ws://127.0.0.1:8000/ws/audio")
    ap.add_argument("--token-file", default=".auth_token")
    ap.add_argument("--mode", choices=["header","query"], default="header")
    args = ap.parse_args()
    token = read_token(args.token_file)
    asyncio.run(run(args.url, token, use_query=(args.mode=="query")))

if __name__ == "__main__":
    main()
