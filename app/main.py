from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool
import os
import shutil

from app.schemas import (
    SummaryRequest,
    DocumentSummaryResponse,
    YouTubeTranscriptRequest,
    YouTubeTranscriptResponse,
    YouTubeSummaryResponse,
)

from app.services.summarizer import (
    summarize_text,
    summarize_text_stream,
)
from app.services.ocr_service import extract_text_from_file
from app.services.whisper_service import transcribe_audio
from app.services.youtube_service import download_youtube_audio

from app.services.youtube_cache import (
    get_cached_transcript,
    save_transcript,
)

app = FastAPI(title="Exam Nector Backend")


# =======================
# HEALTH CHECK
# =======================

@app.get("/")
def health_check():
    return {"status": "Backend is running"}


# =======================
# DOCUMENT SUMMARY
# =======================

@app.post("/summarize/document", response_model=DocumentSummaryResponse)
async def summarize_document(
    file: UploadFile = File(...),
    depth: str = Form(...)
):
    extracted_text = await run_in_threadpool(
        extract_text_from_file, file
    )

    if not extracted_text:
        return DocumentSummaryResponse(
            summary="No readable English text could be extracted from the document.",
            filename=file.filename
        )

    summary = await run_in_threadpool(
        summarize_text, extracted_text, depth
    )

    return DocumentSummaryResponse(
        summary=summary.strip(),
        filename=file.filename
    )


# =======================
# TEST SUMMARY
# =======================

@app.get("/test-summary")
def test_summary():
    return {
        "summary": summarize_text(
            "Artificial intelligence improves productivity by automating repetitive tasks.",
            "easy"
        )
    }


# =======================
# AUDIO / VIDEO TRANSCRIPTION
# =======================

@app.post("/transcribe/audio")
async def transcribe_audio_endpoint(
    file: UploadFile = File(...),
    language: str | None = Form(None)
):
    temp_dir = "app/temp"
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(temp_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = transcribe_audio(file_path, language)

    return {
        "filename": file.filename,
        "text": text
    }


# =======================
# YOUTUBE TRANSCRIPTION
# =======================

@app.post("/transcribe/youtube", response_model=YouTubeTranscriptResponse)
def transcribe_youtube_video(request: YouTubeTranscriptRequest):
    cached = get_cached_transcript(request.youtube_url)

    if cached:
        transcript = cached
    else:
        audio_path = download_youtube_audio(request.youtube_url)
        transcript = transcribe_audio(audio_path)
        save_transcript(request.youtube_url, transcript)

    return YouTubeTranscriptResponse(
        youtube_url=request.youtube_url,
        transcript=transcript
    )


# =======================
# YOUTUBE SUMMARY (NORMAL)
# =======================

@app.post("/summarize/youtube", response_model=YouTubeSummaryResponse)
def summarize_youtube_video(request: SummaryRequest):
    cached = get_cached_transcript(request.youtube_url)

    if cached:
        transcript = cached
    else:
        audio_path = download_youtube_audio(request.youtube_url)
        transcript = transcribe_audio(audio_path)
        save_transcript(request.youtube_url, transcript)

    raw_summary = summarize_text(
        transcript,
        depth=request.depth
    ).strip()

    if request.depth == "easy":
        summary = [
            line.strip("-• ").strip()
            for line in raw_summary.splitlines()
            if line.strip()
        ]
    else:
        summary = raw_summary

    return YouTubeSummaryResponse(
        youtube_url=request.youtube_url,
        summary=summary
    )


# =======================
# YOUTUBE SUMMARY (STREAMING ✨)
# =======================

@app.post("/summarize/youtube/stream")
def stream_youtube_summary(request: SummaryRequest):
    cached = get_cached_transcript(request.youtube_url)

    if cached:
        transcript = cached
    else:
        audio_path = download_youtube_audio(request.youtube_url)
        transcript = transcribe_audio(audio_path)
        save_transcript(request.youtube_url, transcript)

    generator = summarize_text_stream(
        transcript,
        depth=request.depth
    )

    return StreamingResponse(
        generator,
        media_type="text/plain"
    )

# =======================
# DOCUMENT SUMMARY (STREAMING ✨)
# =======================

@app.post("/summarize/document/stream")
async def stream_document_summary(
    file: UploadFile = File(...),
    depth: str = Form(...)
):
    # 1️⃣ OCR (blocking → threadpool)
    extracted_text = await run_in_threadpool(
        extract_text_from_file, file
    )

    if not extracted_text:
        return StreamingResponse(
            iter(["No readable English text could be extracted from the document."]),
            media_type="text/plain",
        )

    # 2️⃣ Stream summary
    generator = summarize_text_stream(
        extracted_text,
        depth=depth,
    )

    return StreamingResponse(
        generator,
        media_type="text/plain",
    )
