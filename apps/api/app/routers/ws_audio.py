from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import time, json

# ws_audio.py
from app.core.config import settings
from ..services import vad as vad_svc
from ..services.provider_chain import asr_chain, llm_chain, tts_chain
from ..services.ws_auth import extract_token_from_ws, verify_token

router = APIRouter()

async def _ws_audio_handler(ws: WebSocket, require_auth: bool):
    user_sub = None

    # 1) Try to auth BEFORE accept (query/header)
    token = extract_token_from_ws(ws) if require_auth else None
    if require_auth and token:
        ok, user_sub = verify_token(token)
        if not ok:
            # fall through to accept-then-auth for a second chance
            token = None
            user_sub = None

    # 2) Accept connection (so client can send token in first message)
    await ws.accept()
    await ws.send_json({"type":"ready"})

    # 3) If still not authed and required, read first control message for token
    if require_auth and user_sub is None:
        try:
            first = await ws.receive()
            txt = first.get("text") if isinstance(first, dict) else None
            if txt:
                try:
                    j = json.loads(txt)
                except Exception:
                    j = {}
                token = j.get("token") or j.get("access_token") or j.get("jwt") or j.get("bearer")
                if token:
                    ok, user_sub = verify_token(token)
                # if the message was not auth, keep it around as potential "start"
                if not token:
                    # push back this first frame into a small buffer
                    pushback = first
                else:
                    pushback = None
            else:
                pushback = first if first.get("bytes") else None
        except Exception:
            pushback = None

        if user_sub is None:
            await ws.close(code=4401)
            return
    else:
        pushback = None

    # ---- Init audio/VAD ----
    sr = settings.WS_SAMPLE_RATE
    frame_ms = settings.VAD_FRAME_MS
    frame_bytes = int(sr * (frame_ms / 1000.0) * 2)  # PCM16 mono

    VAD = getattr(vad_svc, "VAD", None)
    vad = VAD(agg=settings.VAD_AGGRESSIVENESS, frame_ms=frame_ms, sr=sr) if VAD else None

    buf = bytearray()
    utt = bytearray()
    speaking = False
    silence_ms = 0
    start_ts = None
    tts_on = False

    # Unified handshake: accept JSON/text "start" or raw PCM
    try:
        if pushback:
            first = pushback
        else:
            first = await ws.receive()
        if "text" in first and first["text"]:
            txt = first["text"].strip()
            if txt:
                try:
                    _ = json.loads(txt)  # allow {"type":"start", ...}
                except Exception:
                    pass                  # or plain "start"
            await ws.send_json({"type":"partial","text":"(listening...)"})
            # demo greeting for connectivity (no real ASR/TTS needed)
            _demo_text = "Hello (demo transcript)"
            await ws.send_json({"type":"transcript","text":_demo_text})
            await ws.send_json({"event":"COACH_REPLY","text":_demo_text,"citations":[
                {"id":"demo1","title":"Coaching Guide","url":"https://example.com/guide"},
                {"id":"demo2","title":"Role-play Tips","url":"https://example.com/tips"}
            ]})
            await ws.send_json({"event":"TTS_START","text":_demo_text})
            await ws.send_bytes(b"\x00\x00"*4000)
            await ws.send_bytes(b"\x00\x00"*4000)
            await ws.send_json({"event":"TTS_END"})

        elif "bytes" in first and first["bytes"]:
            buf.extend(first["bytes"])
    except Exception:
        await ws.close(code=1000); return

    try:
        while True:
            try:
                if buf:
                    msg = {"bytes": bytes(buf)}
                    buf.clear()
                else:
                    msg = await ws.receive()
            except RuntimeError:
                break

            # control / audio handling continues here...
            if "text" in msg and msg["text"]:
                ...

            # control messages
            if "text" in msg and msg["text"]:
                if msg["text"].strip().upper() == "CANCEL":
                    utt.clear(); speaking=False; silence_ms=0; start_ts=None
                # also allow late auth refresh (rare)
                else:
                    try:
                        j = json.loads(msg["text"])
                        if isinstance(j, dict) and j.get("token"):
                            ok, maybe = verify_token(j["token"])
                            if ok: user_sub = maybe
                    except Exception:
                        pass
                continue

            # audio
            if "bytes" in msg and msg["bytes"] is not None:
                if tts_on:
                    continue  # half-duplex

                buf.extend(msg["bytes"])
                while len(buf) >= frame_bytes:
                    frame = bytes(buf[:frame_bytes]); del buf[:frame_bytes]
                    utt.extend(frame)

                    is_speech = True
                    if vad:
                        try: is_speech = vad.is_speech(frame, sr)
                        except Exception: is_speech = True

                    if is_speech:
                        speaking = True
                        silence_ms = 0
                        if start_ts is None:
                            start_ts = time.time()
                    else:
                        if speaking:
                            silence_ms += frame_ms

                    dur_ms = int((time.time() - start_ts) * 1000) if start_ts else 0
                    utter_end = speaking and (
                        silence_ms >= settings.VAD_MAX_SILENCE_MS
                        or (start_ts and dur_ms >= settings.WS_MAX_UTTER_MS)
                    )

                    if utter_end:
                        pcm16 = bytes(utt)
                        utt.clear(); speaking=False; silence_ms=0; start_ts=None

                        # 1) ASR
                        try:
                            text = await asr_chain.call(pcm16, sr)
                        except Exception as e:
                            await ws.send_json({"event":"ERROR","stage":"ASR","detail":str(e)})
                            continue

                        # 2) LLM
                        try:
                            out = await llm_chain.call({"text": text, "user": user_sub})
                            reply = out.get("text") if isinstance(out, dict) else str(out)
                        except Exception as e:
                            await ws.send_json({"event":"ERROR","stage":"LLM","detail":str(e)})
                            reply = "Sorry, I hit an issue. Try again."

                        # 3) TTS
                        try:
                            await ws.send_json({"event":"TTS_START","text":reply})
                            tts_on = True
                            async for chunk in tts_chain.call(reply):
                                await ws.send_bytes(chunk)
                            await ws.send_json({"event":"TTS_END"})
                        except Exception as e:
                            await ws.send_json({"event":"ERROR","stage":"TTS","detail":str(e)})
                        finally:
                            tts_on = False
                            buf.clear()

    except WebSocketDisconnect:
        return

@router.websocket("/api/ws/audio")   # auth required
async def ws_audio_authed(ws: WebSocket):
    await _ws_audio_handler(ws, require_auth=True)

@router.websocket("/ws/audio")       # legacy open route
async def ws_audio_legacy(ws: WebSocket):
    await _ws_audio_handler(ws, require_auth=False)
