import os
import hashlib

CACHE_DIR = "app/cache/youtube"
os.makedirs(CACHE_DIR, exist_ok=True)


def _video_id_from_url(url: str) -> str:
    """
    Create a stable ID from YouTube URL
    """
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def get_cached_transcript(youtube_url: str) -> str | None:
    video_id = _video_id_from_url(youtube_url)
    cache_path = os.path.join(CACHE_DIR, f"{video_id}.txt")

    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    return None


def save_transcript(youtube_url: str, transcript: str) -> None:
    video_id = _video_id_from_url(youtube_url)
    cache_path = os.path.join(CACHE_DIR, f"{video_id}.txt")

    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(transcript)
