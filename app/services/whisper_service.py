import whisper
import os

# Load model once (VERY IMPORTANT)
model = whisper.load_model("tiny")  # fastest, good enough for summaries


def transcribe_audio(audio_path: str, language: str | None = None) -> str:
    """
    Transcribe audio (webm / m4a / mp3 / wav) directly using Whisper.
    No FFmpeg re-encoding.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError("Audio file not found")

    result = model.transcribe(
        audio_path,
        language=language,  # None = auto-detect
        fp16=False          # REQUIRED on Windows
    )

    return result["text"].strip()
