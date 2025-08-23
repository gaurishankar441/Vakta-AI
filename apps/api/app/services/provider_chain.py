import time
from . import asr_provider, tts_provider, llm_provider
from app.core.config import settings

class ProviderError(Exception): ...

class _Breaker:
    def __init__(self):
        self.failures = 0
        self.last = 0.0
    def can_call(self):
        cool = getattr(settings, "CB_COOLDOWN_SEC", 30)
        return (time.time()-self.last) > cool or self.failures < getattr(settings, "CB_TRIP_AFTER", 3)
    def ok(self):   self.failures = 0
    def fail(self): self.failures += 1; self.last = time.time()

def _build(kind:str):
    if kind=="ASR":
        prefs = getattr(settings,"PREF_ASR","openai,whisperx").split(",")
        impls={"openai": asr_provider.OpenAIASR(), "whisperx": asr_provider.WhisperXASR()}
        fn="complete"
    elif kind=="TTS":
        prefs = getattr(settings,"PREF_TTS","openai,edge").split(",")
        impls={"openai": tts_provider.OpenAITTS(), "edge": tts_provider.EdgeTTS()}
        fn="complete"
    elif kind=="LLM":
        prefs = getattr(settings,"PREF_LLM","openai").split(",")
        impls={"openai": llm_provider.OpenAILLM()}
        fn="complete"
    else:
        raise ValueError(kind)
    chain=[(impls[p.strip()], _Breaker()) for p in prefs if p.strip() in impls]
    return chain, fn

class FallbackChain:
    def __init__(self, kind:str):
        self.chain, self.fn = _build(kind)
    async def call(self, *a, **k):
        last=None
        for impl, br in self.chain:
            if not br.can_call(): continue
            try:
                out = await getattr(impl, self.fn)(*a, **k)
                br.ok(); return out
            except Exception as e:
                br.fail(); last=e
        raise ProviderError(f"{self.fn} failed on all providers: {last}")

asr_chain = FallbackChain("ASR")
tts_chain = FallbackChain("TTS")
llm_chain = FallbackChain("LLM")
