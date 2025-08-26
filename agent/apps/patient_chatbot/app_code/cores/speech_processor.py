class SpeechProcessor:
    """Audio/STT/TTS processing as needed by the app."""

    def transcribe(self, audio_file_path: str) -> dict:
        # TODO: integrate Whisper or provider per SECURITY_POLICIES
        return {"text": "", "confidence": 0.0}

    def synthesize(self, text: str, voice: str | None = None) -> bytes:
        # TODO: integrate TTS provider
        return b""