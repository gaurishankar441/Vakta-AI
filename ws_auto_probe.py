#!/usr/bin/env python3
import asyncio, json, os, re, sys, time, wave, struct

URL = os.environ.get("WS_URL","ws://127.0.0.1:8000/ws/audio")
WS_FILE_PATH = os.environ["WS_FILE_PATH"]
WAV="test_16k.wav"; CHUNK=3200; TIMEOUT=float(os.environ.get("WS_RECV_TIMEOUT","120"))

code = open(WS_FILE_PATH, "r", encoding="utf-8").read()

# find likely end-control tokens mentioned in code
cands = set(re.findall(r'["\'](finalize|finalizing|stop|done|end|eof|finish|close|final|eos)["\']', code, flags=re.I))
if re.search(r'evt\.get\(\s*["\']finalize["\']\s*\)\s*(?:is\s*True|==\s*True)', code):
    cands.add("finalize:true-key")

order = ["finalize","finalizing","stop","done","end","eof","finish","close","final","eos","finalize:true-key"]
tokens = [t for t in order if t in cands]
print("[probe] tokens from server code:", tokens or "(none)")

# make sure we have a test wav
def ensure_wav():
    try:
        with wave.open(WAV,"rb") as wf:
            assert wf.getframerate()==16000 and wf.getnchannels()==1 and wf.getsampwidth()==2
            return
    except Exception:
        pass
    with wave.open(WAV,'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        for i in range(16000):
            w.writeframes(struct.pack('<h', int(0.3*32767*__import__("math").sin(2*__import__("math").pi*440*i/16000))))
ensure_wav()

def read_pcm():
    with wave.open(WAV,"rb") as wf:
        return wf.readframes(wf.getnframes())

async def run():
    pcm=read_pcm()
    headers={}
    tok=os.environ.get("WS_BEARER_TOKEN")
    if tok: headers["Authorization"]="Bearer "+tok

    async with (await __import__("websockets").connect(URL, max_size=None, extra_headers=headers)) as ws:
        # start
        await ws.send(json.dumps({"type":"start","sample_rate":16000,"channels":1,"format":"pcm_s16le"}))
        # bytes
        for i in range(0,len(pcm),CHUNK): await ws.send(pcm[i:i+CHUNK])
        # empty-binary sentinel
        try:
            await ws.send(b"")
            print("[->] empty-binary")
        except Exception as e:
            print("[i] empty-binary not supported:", e)

        # send parsed tokens (or fallback list)
        send_list = tokens[:] if tokens else ["finalize","finalizing","stop","done","end","eof","finish","close"]
        for t in send_list:
            payload = {"finalize": True} if t=="finalize:true-key" else {"type": t}
            await ws.send(json.dumps(payload))
            print("[->]", payload)
            await asyncio.sleep(0.15)

        # tiny text tick as last resort
        try:
            await ws.send(" ")
            print("[->] tick ' '")
        except Exception:
            pass

        # read & save tts
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
                print("[<-text]", str(msg)[:120].replace("\n","\\n"))
                continue
            t=evt.get("type"); 
            if t=="warn":
                print("[warn]",evt.get("message")); continue
            print("[<-]", json.dumps(evt))
            if t=="tts":
                fmt=evt.get("format","mp3")
                out_path=f"/tmp/tts_out.{fmt}"; out=open(out_path,"wb")
            if t in ("tts_end","error","closed"):
                break
        if out:
            out.close(); print("[save]", out_path)
        else:
            print("[save] no TTS received")
asyncio.run(run())
