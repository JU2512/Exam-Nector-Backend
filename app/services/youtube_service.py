# app/services/youtube_service.py

import os
import uuid
import subprocess
import glob

TEMP_DIR = "app/temp/youtube"

def download_youtube_audio(youtube_url: str) -> str:
    """
    Reliable YouTube audio/video download for Windows.
    No cookies. Android client. Whisper-compatible.
    """

    os.makedirs(TEMP_DIR, exist_ok=True)

    file_id = str(uuid.uuid4())
    output_template = os.path.join(TEMP_DIR, file_id)

    cmd = [
        "yt-dlp",

        # ✅ KEY FIX
        "--extractor-args", "youtube:player_client=android",

        # ✅ Allow safe fallback formats
        "-f", "bestaudio[ext=m4a]/bestaudio[ext=webm]/best",

        "--no-playlist",
        "--force-ipv4",
        "--geo-bypass",

        "-o", f"{output_template}.%(ext)s",

        youtube_url,
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "This YouTube video cannot be summarized due to restrictions."
        )

    files = glob.glob(f"{output_template}.*")

    if not files:
        raise RuntimeError("No downloadable media found")

    return files[0]  # mp4 / webm / m4a → Whisper can read directly
