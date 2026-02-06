import os
import uuid
import subprocess
import glob

TEMP_DIR = "app/temp/youtube"

def download_youtube_audio(youtube_url: str) -> str:
    """
    Downloads YouTube audio in a Whisper-compatible format
    WITHOUT ffmpeg conversion.
    """

    os.makedirs(TEMP_DIR, exist_ok=True)

    audio_id = str(uuid.uuid4())
    output_template = os.path.join(TEMP_DIR, audio_id)

    download_cmd = [
        "yt-dlp",

        # ✅ Explicitly avoid SABR / encrypted streams
        "-f", "bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio",

        # ✅ Stability flags
        "--no-playlist",
        "--force-ipv4",
        "--geo-bypass",

        # Output
        "-o", f"{output_template}.%(ext)s",

        youtube_url,
    ]

    try:
        subprocess.run(
            download_cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Failed to download YouTube audio") from e

    audio_files = glob.glob(f"{output_template}.*")

    if not audio_files:
        raise RuntimeError("No audio file downloaded")

    return audio_files[0]  # ✅ fed directly to Whisper
