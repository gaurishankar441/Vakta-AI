from celery import shared_task

@shared_task(name="tasks.tts_jobs.synthesize_tts")
def synthesize_tts(text:str, lang:str="en"):
    # TODO: call real TTS; stub returns meta
    return {"ok": True, "len": len(text), "lang": lang}
