import whisper
import os
import subprocess
import uuid

TEMP_DIR = "app/temp"

# Load model once (VERY IMPORTANT)
model = whisper.load_model("base")  # base = fast + accurate


def extract_audio(video_path: str) -> str:
    """
    Extract audio from video using FFmpeg
    """
    os.makedirs(TEMP_DIR, exist_ok=True)

    audio_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.wav")

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if result.returncode != 0:
        raise RuntimeError("FFmpeg audio extraction failed")

    return audio_path


def transcribe_audio(audio_path: str, language: str | None = None) -> str:
    """
    Transcribe audio to text using Whisper
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError("Audio file not found")

    result = model.transcribe(
        audio_path,
        language=language,  # None = auto-detect
        fp16=False          # REQUIRED on Windows
    )

    return result["text"].strip()
