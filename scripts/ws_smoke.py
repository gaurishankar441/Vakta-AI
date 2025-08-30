#!/usr/bin/env python3
import asyncio, json, os, sys, time, wave
import websockets  # pip install websockets

URL=os.environ.get("WS_URL","ws://127.0.0.1:8000/ws/audio")
WAV=os.environ.get("WS_WAV","test_16k.wav")
TIMEOUT=float(os.environ.get("WS_RECV_TIMEOUT","90"))
CHUNK=3200  # 100ms @16k mono s16le

def ensure_wav(path:str):
    if os.path.exists(path): return
    import struct, math
    with wave.open(path,'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        for i in range(16000):
            w.writeframes(struct.pack('<h', int(0.3*32767*math.sin(2*math.pi*440*i/16000))))

def read_pcm(path:str)->bytes:
    with wave.open(path,"rb") as wf:
        assert wf.getframerate()==16000 and wf.getnchannels()==1 and wf.getsampwidth()==2, "need 16kHz mono pcm_s16le WAV"
        return wf.readframes(wf.getnframes())

async def main():
    ensure_wav(WAV)
    pcm=read_pcm(WAV)
    headers={}
    tok=os.environ.get("WS_BEARER_TOKEN")
    if tok: headers["Authorization"]=f"Bearer {tok}"

    async with websockets.connect(URL, max_size=None) as ws:
        # start
        await ws.send(json.dumps({"type":"start","sample_rate":16000,"channels":1,"format":"pcm_s16le"}))
        # audio
        for i in range(0,len(pcm),CHUNK):
            await ws.send(pcm[i:i+CHUNK])

        # EOS burst (server-compatible)
        try: await ws.send(b"")
        except Exception: pass
        for payload in ({"type":"finalizing"},{"event":"finalizing"}):
            await ws.send(json.dumps(payload)); await asyncio.sleep(0.10)
        for txt in ("finalizing"," "):  # plain token + tick
            try: await ws.send(txt); await asyncio.sleep(0.10)
            except Exception: pass
        await ws.send(json.dumps({"type":"end"})); await asyncio.sleep(0.10)
        try: await ws.send("end")
        except Exception: pass
        try: await ws.ping()
        except Exception: pass

        # receive & save TTS
        deadline=time.time()+TIMEOUT
        out=None; out_path=None
        while time.time()<deadline:
            try:
                msg=await asyncio.wait_for(ws.recv(), timeout=max(0.1,deadline-time.time()))
            except asyncio.TimeoutError:
                print("[i] recv timeout"); break
            if isinstance(msg,(bytes,bytearray)):
                if out: out.write(msg)
                continue
            try:
                evt=json.loads(msg)
            except Exception:
                continue
            t=evt.get("type")
            if t=="warn": continue
            print("[<-]", json.dumps(evt))
            if t=="tts":
                fmt=evt.get("format","mp3")
                out_path=f"/tmp/tts_out.{fmt}"
                out=open(out_path,"wb")
            if t in ("tts_end","error","closed"):
                break

        if out:
            out.close()
            print("[save]", out_path)
            if os.environ.get("WS_OPEN")=="1" and sys.platform=="darwin":
                os.system(f"open {out_path}")
        else:
            print("[save] no TTS received")

if __name__=="__main__":
    asyncio.run(main())
