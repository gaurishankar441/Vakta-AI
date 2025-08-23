class VADService:
    def is_speech(self, pcm: bytes)->bool:
        # naive: any non-zero byte => speech
        return any(pcm)
