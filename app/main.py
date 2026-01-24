from fastapi import FastAPI, UploadFile, File, Form
from app.services.summarizer import summarize_text
from app.services.ocr_service import extract_text_from_file
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

from app.services.whisper_service import (
    extract_audio,
    transcribe_audio,
)

from app.services.youtube_service import download_youtube_audio

app = FastAPI(title="Exam Nector Backend")


# =======================
# HEALTH CHECK
# =======================

@app.get("/")
def health_check():
    return {"status": "Backend is running"}


# =======================
# DOCUMENT SUMMARY (MOCK)
# =======================

# =======================
# DOCUMENT SUMMARY (OCR + AI)
# =======================

@app.post("/summarize/document", response_model=DocumentSummaryResponse)
async def summarize_document(
    file: UploadFile = File(...),
    depth: str = Form(...)
):
    # Run OCR in threadpool
    extracted_text = await run_in_threadpool(
        extract_text_from_file, file
    )

    if not extracted_text:
        return DocumentSummaryResponse(
            summary="No readable English text could be extracted from the document.",
            filename=file.filename
        )

    # Run summarization in threadpool
    summary = await run_in_threadpool(
        summarize_text, extracted_text, depth
    )

    return DocumentSummaryResponse(
        summary=summary.strip(),
        filename=file.filename
    )




# =======================
# WHISPER AUDIO TRANSCRIPTION
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

    # Video → extract audio
    if file.content_type and file.content_type.startswith("video"):
        audio_path = extract_audio(file_path)
    else:
        audio_path = file_path

    text = transcribe_audio(audio_path, language)

    return {
        "filename": file.filename,
        "text": text
    }


# =======================
# YOUTUBE TRANSCRIPTION
# =======================

@app.post("/transcribe/youtube", response_model=YouTubeTranscriptResponse)
def transcribe_youtube_video(request: YouTubeTranscriptRequest):
    audio_path = download_youtube_audio(request.youtube_url)
    transcript = transcribe_audio(audio_path)

    return YouTubeTranscriptResponse(
        youtube_url=request.youtube_url,
        transcript=transcript
    )


# =======================
# YOUTUBE SUMMARY (FINAL PIPELINE)
# =======================

@app.post("/summarize/youtube", response_model=YouTubeSummaryResponse)
def summarize_youtube_video(request: SummaryRequest):
    """
    YouTube → Whisper → Ollama → Structured Summary
    """

    # Step 1: Transcribe
    audio_path = download_youtube_audio(request.youtube_url)
    transcript = transcribe_audio(audio_path)

    # Step 2: Summarize (raw text)
    raw_summary = summarize_text(transcript, depth=request.depth).strip()

    # Step 3: Format based on depth
    if request.depth == "easy":
        summary = [
            line.strip("-• ").strip()
            for line in raw_summary.splitlines()
            if line.strip()
        ]
    elif request.depth == "medium":
        summary = raw_summary  # preserve headings & structure
    else:  # long
        summary = raw_summary  # full detailed notes

    return YouTubeSummaryResponse(
        youtube_url=request.youtube_url,
        summary=summary
    )
