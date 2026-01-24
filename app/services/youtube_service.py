import os
import uuid
import subprocess
import glob

TEMP_DIR = "app/temp/youtube"


def download_youtube_audio(youtube_url: str) -> str:
    """
    Downloads YouTube audio and converts it to WAV (16kHz mono).
    Returns path to WAV file.
    """

    os.makedirs(TEMP_DIR, exist_ok=True)

    audio_id = str(uuid.uuid4())
    output_template = os.path.join(TEMP_DIR, audio_id)

    # Step 1: Download best audio (any format)
    download_cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "-o", f"{output_template}.%(ext)s",
        youtube_url
    ]

    try:
        subprocess.run(download_cmd, check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError("Failed to download YouTube audio")

    # Step 2: Detect downloaded audio file
    audio_files = glob.glob(f"{output_template}.*")
    audio_files = [f for f in audio_files if not f.endswith(".wav")]

    if not audio_files:
        raise RuntimeError("No audio file downloaded")

    input_audio = audio_files[0]
    wav_path = f"{output_template}.wav"

    # Step 3: Convert to WAV (16kHz mono)
    convert_cmd = [
        "ffmpeg",
        "-y",
        "-i", input_audio,
        "-ac", "1",
        "-ar", "16000",
        wav_path
    ]

    try:
        subprocess.run(convert_cmd, check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError("Failed to convert audio to WAV")

    return wav_path
