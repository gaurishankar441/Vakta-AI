#!/usr/bin/env python3
import asyncio, json, os, sys, wave, time, struct, math
import websockets

URL=os.environ.get("WS_URL","ws://127.0.0.1:8000/ws/audio")
WAV="test_16k.wav"; CHUNK=3200; TIMEOUT=float(os.environ.get("WS_RECV_TIMEOUT","90"))

# ensure 1s/16k mono test wav
if not os.path.exists(WAV):
    with wave.open(WAV,'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        for i in range(16000):
            w.writeframes(struct.pack('<h', int(0.3*32767*math.sin(2*math.pi*440*i/16000))))

def rd(path):
    with wave.open(path,"rb") as wf:
        assert wf.getframerate()==16000 and wf.getnchannels()==1 and wf.getsampwidth()==2, "need 16k/mono/s16le"
        return wf.readframes(wf.getnframes())

async def main():
    pcm=rd(WAV)
    headers={}
    tok=os.environ.get("WS_BEARER_TOKEN")
    if tok: headers["Authorization"]="Bearer "+tok

    async with websockets.connect(URL, max_size=None) as ws:
        # 1) start
        await ws.send(json.dumps({"type":"start","sample_rate":16000,"channels":1,"format":"pcm_s16le"}))

        # 2) audio bytes
        for i in range(0,len(pcm),CHUNK):
            await ws.send(pcm[i:i+CHUNK])

        # 3) attempt multiple end signals (from server code: finalizing, end, close)
        seq = []
        for key in ("event","type"):
            for val in ("finalizing","end","close"):
                seq.append({key: val})
        plaintext = ["finalizing","end","close"]

        # zero-length binary sentinel first
        try:
            await ws.send(b"")
            print("[->] empty-binary")
        except Exception as e:
            print("[i] empty-binary not supported:", e)

        # JSON variants
        for payload in seq:
            await ws.send(json.dumps(payload))
            print("[->json]", payload)
            await asyncio.sleep(0.12)

        # plain-text variants
        for t in plaintext:
            await ws.send(t)
            print("[->text]", t)
            await asyncio.sleep(0.12)

        # ping (some servers wake on ping)
        try:
            await ws.ping()
            print("[->] ping()")
        except Exception:
            pass

        # 4) receive & save TTS
        deadline=time.time()+TIMEOUT
        out=None; out_path=None
        while time.time()<deadline:
            try:
                msg=await asyncio.wait_for(ws.recv(), timeout=max(0.1,deadline-time.time()))
            except asyncio.TimeoutError:
                print("[i] recv timeout"); break

            if isinstance(msg,(bytes,bytearray)):
                if out: out.write(msg)
                else: print(f"[<-bin] {len(msg)} bytes (no file open yet)")
                continue

            try:
                evt=json.loads(msg)
            except Exception:
                print("[<-text]", str(msg)[:200].replace("\n","\\n"))
                continue

            t=evt.get("type")
            if t=="warn":
                print("[warn]", evt.get("message")); continue
            print("[<-]", json.dumps(evt))
            if t=="tts":
                fmt=evt.get("format","mp3")
                out_path=f"/tmp/tts_out.{fmt}"
                out=open(out_path,"wb")
            if t in ("tts_end","error","closed"):
                break

        if out:
            out.close(); print("[save]", out_path)
        else:
            print("[save] no TTS received")
asyncio.run(main())
